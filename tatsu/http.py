from __future__ import annotations

import asyncio
import logging
import sys
from collections.abc import Coroutine
from datetime import datetime, timezone
from importlib import metadata
from typing import Any, ClassVar, Literal
from urllib.parse import quote as uriquote, urljoin

import aiohttp

from .errors import BadRequest, Forbidden, HTTPException, NotFound, TatsuServerError
from .hooks import GEN_DECODER, GEN_ENCODER


_LOGGER = logging.getLogger(__name__)


class Route:
    """A helper class for instantiating an HTTP method to Tatsu.

    Parameters
    ----------
    method: :class:`str`
        The HTTP request to make, e.g. ``"GET"``.
    path: :class:`str`
        The prepended path to the API endpoint you want to hit, e.g. ``"/user/{user_id}/profile"``.
    **parameters: Any
        Special keyword arguments that will be substituted into the corresponding spot in the `path` where the key is
        present, e.g. if your parameters are ``user_id=1234`` and your path is``"user/{user_id}/profile"``, the path
        will become ``"user/1234/profile"``.
    """

    BASE: ClassVar[str] = "https://api.tatsu.gg/v1/"

    def __init__(self, method: str, path: str, **parameters: Any) -> None:
        self.method = method
        self.path = path
        url = urljoin(self.BASE, path)
        if parameters:
            url = url.format_map({k: uriquote(v) if isinstance(v, str) else v for k, v in parameters.items()})
        self.url = url


class HTTPClient:
    """A small HTTP client that sends requests to the Tatsu API."""

    def __init__(self, token: str, *, session: aiohttp.ClientSession | None = None) -> None:
        self.token = token
        self._session = session
        user_agent = "Tatsu (https://github.com/Sachaa-Thanasius/Tatsu {0} Python/{1[0]}.{1[1]} aiohttp/{2}"
        self.user_agent = user_agent.format(metadata.version("tatsu"), sys.version_info, metadata.version("aiohttp"))
        self._ratelimit_unlock = asyncio.Event()
        self._ratelimit_unlock.set()
        self._ratelimit_reset_dt = None

    async def _start_session(self) -> None:
        """|coro|

        Create an internal HTTP session for this client if necessary.
        """

        if (not self._session) or self._session.closed:
            self._session = aiohttp.ClientSession()

    async def close(self) -> None:
        """|coro|

        Close the internal HTTP session.
        """

        if self._session and not self._session.closed:
            await self._session.close()

    async def request(self, route: Route, **kwargs: Any) -> bytes:
        """|coro|

        Send an HTTP request to some endpoint in the Tatsu API.

        Parameters
        ----------
        route
            The filled-in API route that will be sent a request.
        **kwargs
            Arbitrary keyword arguments for :meth:`aiohttp.ClientSession.request`. See that method for more information.
        """

        headers = kwargs.pop("headers", {})
        headers["User-Agent"] = self.user_agent
        headers["Authorization"] = self.token
        kwargs["headers"] = headers

        await self._start_session()
        assert self._session

        if not self._ratelimit_unlock.is_set():
            await self._ratelimit_unlock.wait()

        response: aiohttp.ClientResponse | None = None
        message: str | dict[str, Any] | None = None
        for _tries in range(5):
            async with self._session.request(route.method, route.url, **kwargs) as response:
                _LOGGER.debug("%s %s has returned %d.", route.method, response.url.human_repr(), response.status)

                data = await response.read()
                _LOGGER.debug(data)

                limit = response.headers.get("X-RateLimit-Limit")
                remaining = response.headers.get("X-RateLimit-Remaining")
                reset = response.headers.get("X-RateLimit-Reset", 0.0)
                reset_dt = datetime.fromtimestamp(float(reset), tz=timezone.utc).astimezone()

                msg = "Rate limit info: limit=%s, remaining=%s, reset=%s (tries=%s)"
                _LOGGER.debug(msg, limit, remaining, reset_dt, _tries)

                if not self._ratelimit_reset_dt or self._ratelimit_reset_dt < reset_dt:
                    self._ratelimit_reset_dt = reset_dt

                if response.status != 429 and remaining == "0":
                    now = datetime.now(tz=timezone.utc).astimezone()
                    self._ratelimit_unlock.clear()
                    wait_delta = self._ratelimit_reset_dt - now
                    _LOGGER.info("Emptied the ratelimit. Waiting for %s seconds for reset.", wait_delta.total_seconds())
                    await asyncio.sleep(wait_delta.total_seconds())
                    self._ratelimit_unlock.set()

                if 300 > response.status >= 200:
                    return data

                message = GEN_DECODER.decode(data)

                if response.status == 429:
                    now = datetime.now(tz=timezone.utc).astimezone()
                    self._ratelimit_unlock.clear()
                    _LOGGER.debug(
                        "Comparison of timestamps (now vs. ratelimit reset time): %s vs %s",
                        now,
                        self._ratelimit_reset_dt,
                    )
                    wait_delta = self._ratelimit_reset_dt - now
                    _LOGGER.info("Hit a rate limit. Waiting for %s seconds for reset.", wait_delta.total_seconds())
                    await asyncio.sleep(wait_delta.total_seconds())
                    self._ratelimit_unlock.set()
                    continue

                if response.status == 400:
                    raise BadRequest(response, message)
                if response.status == 403:
                    raise Forbidden(response, message)
                if response.status == 404:
                    raise NotFound(response, message)
                if response.status >= 500:
                    raise TatsuServerError(response, message)

                raise HTTPException(response, message)

        if response is not None:
            _LOGGER.debug("Reached maximum number of retries.")
            raise HTTPException(response, message)

        msg = "Unreachable code in HTTP handling."
        raise RuntimeError(msg)

    def get_guild_member_points(self, guild_id: int, member_id: int) -> Coroutine[Any, Any, bytes]:
        route = Route("GET", "guilds/{guild_id}/members/{member_id}/points", guild_id=guild_id, member_id=member_id)
        return self.request(route)

    def modify_guild_member_points(
        self,
        guild_id: int,
        member_id: int,
        action: int,
        amount: int,
    ) -> Coroutine[Any, Any, bytes]:
        # Note: Points amount cannot be more than 100,000.
        route = Route("PATCH", "guilds/{guild_id}/members/{member_id}/points", guild_id=guild_id, member_id=member_id)
        data = GEN_ENCODER.encode({"action": action, "amount": amount})
        return self.request(route, data=data)

    def modify_guild_member_score(
        self,
        guild_id: int,
        member_id: int,
        action: int,
        amount: int,
    ) -> Coroutine[Any, Any, bytes]:
        # Note: Score amount cannot be more than 100,000.
        route = Route("PATCH", "guilds/{guild_id}/members/{member_id}/score", guild_id=guild_id, member_id=member_id)
        data = GEN_ENCODER.encode({"action": action, "amount": amount})
        return self.request(route, data=data)

    def get_guild_member_ranking(
        self,
        guild_id: int,
        user_id: int,
        period: Literal["all", "month", "week"] = "all",
    ) -> Coroutine[Any, Any, bytes]:
        route = Route(
            "GET",
            "guilds/{guild_id}/rankings/members/{user_id}/{time_range}",
            guild_id=guild_id,
            user_id=user_id,
            time_range=period,
        )
        return self.request(route)

    def get_guild_rankings(
        self,
        guild_id: int,
        period: Literal["all", "month", "week"] = "all",
        *,
        offset: int = 0,
    ) -> Coroutine[Any, Any, bytes]:
        # Note: Pagination offset must be greater than or equal to 0.
        route = Route("GET", "guilds/{guild_id}/rankings/{time_range}", guild_id=guild_id, time_range=period)
        params = {"offset": offset}
        return self.request(route, params=params)

    def get_user_profile(self, user_id: int) -> Coroutine[Any, Any, bytes]:
        route = Route("GET", "users/{user_id}/profile", user_id=user_id)
        return self.request(route)

    def get_store_listing(self, listing_id: str) -> Coroutine[Any, Any, bytes]:
        route = Route("GET", "store/listings/{listing_id}", listing_id=listing_id)
        return self.request(route)
