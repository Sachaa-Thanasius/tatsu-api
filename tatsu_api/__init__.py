"""
Tatsu API Wrapper
-----------------

A basic unofficial wrapper for the Tatsu API.
"""

from __future__ import annotations

import asyncio
import itertools
import logging
import sys
from collections.abc import Coroutine
from datetime import datetime, timezone
from enum import Enum
from importlib.metadata import version as im_version
from typing import TYPE_CHECKING, Any, ClassVar, Literal
from urllib.parse import quote as uriquote

import aiohttp
import msgspec


if TYPE_CHECKING:
    from types import TracebackType

    from typing_extensions import Self
else:

    class TracebackType:
        pass

    class Self:
        pass


# ==== Enums


__all__ = (
    "ActionType",
    "SubscriptionType",
    "CurrencyType",
    "TatsuException",
    "HTTPException",
    "BadRequest",
    "Forbidden",
    "NotFound",
    "RateLimited",
    "TatsuServerError",
    "GuildMemberPoints",
    "GuildMemberScore",
    "GuildMemberRanking",
    "Ranking",
    "GuildRankings",
    "User",
    "StorePrice",
    "StoreListing",
    "Client",
)


class ActionType(Enum):
    """The way to modify a Tatsu user's score."""

    ADD = 0
    REMOVE = 1


class SubscriptionType(Enum):
    """The type of Tatsu subscription a user has."""

    NONE = 0
    SUPPORTER1 = 1
    SUPPORTER2 = 2
    SUPPORTER3 = 3


class CurrencyType(Enum):
    """A type of Tatsu currency."""

    CREDITS = 0
    TOKENS = 1
    EMERALDS = 2
    CANDY_CANE = 3
    USD = 4
    CANDY_CORN = 5


# ==== Exceptions


class TatsuException(Exception):
    """Base exception class for Tatsu."""


class HTTPException(TatsuException):
    """Exception that's raised when a non-200 HTTP status code is returned.

    Parameters
    ----------
    response: :class:`aiohttp.ClientResponse`
        The HTTP response from the request.
    message: :class:`str` | dict[:class:`str`, Any], optional
        The decoded response data.

    Attributes
    ----------
    response: :class:`aiohttp.ClientResponse`
        The HTTP response from the request.
    status: :class:`int`
        The HTTP status of the response.
    code: :class:`int`
        The Tatsu-specific error code.
    text: :class:`str`
        The Tatsu-specific error text.
    """

    def __init__(self, response: aiohttp.ClientResponse, message: str | dict[str, Any] | None) -> None:
        self.response = response
        self.status: int = response.status
        self.code: int = message.get("code", 0) if isinstance(message, dict) else 0
        self.text: str = message.get("message", "") if isinstance(message, dict) else (message or "")

        fmt = "{0.status} {0.reason} (error code: {1})"
        if len(self.text):
            fmt += ": {2}"

        super().__init__(fmt.format(self.response, self.code, self.text))


class BadRequest(HTTPException):
    """Exception that's raised when status code 400 occurs.

    Subclass of :exc:`HTTPException`.
    """


class Forbidden(HTTPException):
    """Exception that's raised when status code 403 occurs.

    Subclass of :exc:`HTTPException`.
    """


class NotFound(HTTPException):
    """Exception that's raised when status code 404 occurs.

    Subclass of :exc:`HTTPException`.
    """


class RateLimited(HTTPException):
    """Exception that's raised when status code 429 occurs.

    Subclass of :exc:`HTTPException`.
    """


class TatsuServerError(HTTPException):
    """Exception that's raised when a 500 range status code occurs.

    Subclass of :exc:`HTTPException`.
    """


# ==== Models


__all__ = (
    "GuildMemberPoints",
    "GuildMemberScore",
    "GuildMemberRanking",
    "Ranking",
    "GuildRankings",
    "User",
    "StorePrice",
    "StoreListing",
)


class GuildMemberPoints(msgspec.Struct, frozen=True):
    """A Discord guild member's points information.

    Parameters
    ----------
    guild_id: :class:`str`
        The Discord ID of the guild.
    points: :class:`int`
        The user's points.
    rank: :class:`int`
        The user's rank based on their points.
    user_id: :class:`str`
        The user's Discord ID.
    """

    guild_id: str
    points: int
    rank: int
    user_id: str


class GuildMemberScore(msgspec.Struct, frozen=True):
    """A Discord guild member's score information.

    Parameters
    ----------
    guild_id: :class:`str`
        The Discord ID of the guild.
    score: :class:`int`
        The user's score.
    user_id: :class:`str`
        The user's Discord ID.
    """

    guild_id: str
    score: int
    user_id: str


class GuildMemberRanking(msgspec.Struct, frozen=True):
    """A Discord guild member's ranking information over some period of time.

    Attributes
    ----------
    guild_id: :class:`str`
        The Discord ID of the guild.
    rank: :class:`int`
        The user's rank.
    score: :class:`int`
        The user's score.
    user_id: :class:`str`
        The user's Discord ID.
    """

    guild_id: str
    rank: int
    score: int
    user_id: str


class Ranking(msgspec.Struct, frozen=True):
    """A generic rank information object.

    Attributes
    ----------
    rank: :class:`int`
        The user's rank.
    score: :class:`int`
        The user's score.
    user_id: :class:`str`
        The user's Discord ID.
    """

    rank: int
    score: int
    user_id: str


class GuildRankings(msgspec.Struct, frozen=True):
    """All the rankings in a guild over some period of time.

    Attributes
    ----------
    guild_id: :class:`str`
        The Discord ID of the guild.
    rankings: tuple[:class:`Ranking`, ...]
        The rankings.
    """

    guild_id: str
    rankings: tuple[Ranking, ...] = msgspec.field(default_factory=tuple)


class User(msgspec.Struct, frozen=True):
    """A Tatsu-bot user.

    Attributes
    ----------
    avatar_hash: class:`str`
        The user's Discord avatar hash.
    avatar_url: class:`str`
        The user's Discord avatar URL.
    credits: :class:`int`
        The amount of credits the user has.
    discriminator: class:`str`
        The user's 4 digit discriminator.
    id: class:`str`
        The user's Discord ID.
    info_box: class:`str`
        The text in the user's info box.
    reputation: :class:`int`
        The number of reputation points the user has.
    subscription_type: :class:`int`
        The user's subscription type.
    subscription_renewal: :class:`str`, optional
        The subscription renewal time if the user has a subscription. Optional
    title: class:`str`
        The text in the user's title.
    tokens: :class:`int`
        The amount of tokens the user has.
    username: class:`str`
        The user's Discord username.
    xp: :class:`int`
        The number of experience points the user has.
    """

    avatar_hash: str
    avatar_url: str
    credits: int
    discriminator: str
    id: str
    info_box: str
    reputation: int
    subscription_type: SubscriptionType
    title: str
    tokens: int
    username: str
    xp: int
    subscription_renewal: datetime | None = None


class StorePrice(msgspec.Struct, frozen=True):
    """A price of a Tatsu store item.

    Attributes
    ----------
    currency: :class:`CurrencyType`
        The currency type.
    amount: :class:`float`
        The cost of the item in the currency.
    """

    currency: CurrencyType
    amount: float


class StoreListing(msgspec.Struct, frozen=True):
    """The listing of a Tatsu store item.

    Attributes
    ----------
    id: :class:`str`
        The ID of the store listing.
    name: :class:`str
        The name of the item.
    summary: :class:`str
        The summary of the item.
    description: :class:`str
        The description of the item.
    new: :class:`str
        Whether this is a new item in the store.
    preview: :class:`str`, optional
        The URL to an image preview of the item. Optional.
    prices: tuple[:class:`StorePrice`, ...], optional
        The prices for the item. Optional.
    categories: tuple[: :class:`str`, ...], optional
        The categories for the item. Optional
    tags: tuple[: :class:`str`, ...], optional
        The tags for the item. Optional.
    """

    id: str
    name: str
    summary: str
    description: str
    new: bool
    preview: str | None = None
    prices: tuple[StorePrice, ...] = msgspec.field(default_factory=tuple)
    categories: tuple[str, ...] = msgspec.field(default_factory=tuple)
    tags: tuple[str, ...] = msgspec.field(default_factory=tuple)


# fmt: off
GEN_ENCODER                     = msgspec.json.Encoder()
GEN_DECODER                     = msgspec.json.Decoder()
GUILD_MEMBER_POINTS_DECODER     = msgspec.json.Decoder(GuildMemberPoints)
GUILD_MEMBER_SCORE_DECODER      = msgspec.json.Decoder(GuildMemberScore)
GUILD_MEMBER_RANKING_DECODER    = msgspec.json.Decoder(GuildMemberRanking)
GUILD_RANKINGS_DECODER          = msgspec.json.Decoder(GuildRankings)
USER_DECODER                    = msgspec.json.Decoder(User)
STORE_LISTING_DECODER           = msgspec.json.Decoder(StoreListing)
# fmt: on


# ==== Raw HTTP Client


_LOGGER = logging.getLogger(__name__)


class Route:
    """A helper class for instantiating an HTTP method to Tatsu.

    Parameters
    ----------
    method: :class:`str`
        The HTTP request to make, e.g. ``"GET"``.
    path: :class:`str`
        The prepended path to the API endpoint you want to hit, e.g. ``"/user/{user_id}/profile"``.
    **parameters: object
        Special keyword arguments that will be substituted into the corresponding spot in the `path` where the key is
        present, e.g. if your parameters are ``user_id=1234`` and your path is``"user/{user_id}/profile"``, the path
        will become ``"user/1234/profile"``.
    """

    BASE: ClassVar[str] = "https://api.tatsu.gg/v1"

    def __init__(self, method: str, path: str, **parameters: object) -> None:
        self.method = method
        self.path = path
        url = self.BASE + path
        if parameters:
            url = url.format_map({k: uriquote(v) if isinstance(v, str) else v for k, v in parameters.items()})
        self.url = url


class HTTPClient:
    """A small HTTP client that sends requests to the Tatsu API."""

    def __init__(self, token: str, *, session: aiohttp.ClientSession | None = None) -> None:
        self.token = token
        self._session = session
        user_agent = "Tatsu (https://github.com/Sachaa-Thanasius/Tatsu {0} Python/{1[0]}.{1[1]} aiohttp/{2}"
        self.user_agent = user_agent.format(im_version("tatsu"), sys.version_info, im_version("aiohttp"))
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
        route = Route("GET", "/guilds/{guild_id}/members/{member_id}/points", guild_id=guild_id, member_id=member_id)
        return self.request(route)

    def modify_guild_member_points(
        self,
        guild_id: int,
        member_id: int,
        action: int,
        amount: int,
    ) -> Coroutine[Any, Any, bytes]:
        # Note: Points amount cannot be more than 100,000.
        route = Route("PATCH", "/guilds/{guild_id}/members/{member_id}/points", guild_id=guild_id, member_id=member_id)
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
        route = Route("PATCH", "/guilds/{guild_id}/members/{member_id}/score", guild_id=guild_id, member_id=member_id)
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
            "/guilds/{guild_id}/rankings/members/{user_id}/{time_range}",
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
        route = Route("GET", "/guilds/{guild_id}/rankings/{time_range}", guild_id=guild_id, time_range=period)
        params = {"offset": offset}
        return self.request(route, params=params)

    def get_user_profile(self, user_id: int) -> Coroutine[Any, Any, bytes]:
        route = Route("GET", "/users/{user_id}/profile", user_id=user_id)
        return self.request(route)

    def get_store_listing(self, listing_id: str) -> Coroutine[Any, Any, bytes]:
        route = Route("GET", "/store/listings/{listing_id}", listing_id=listing_id)
        return self.request(route)


# ==== User-facing client


class Client:
    """The client that is used to handle interaction with the Tatsu API.

    Parameters
    ----------
    token: :class:`str`
        The Tatsu API key that will be used to authorize all requests to it.
    session: :class:`aiohttp.ClientSession`, optional
        A web client session to use for connecting to the API. If provided, the library is not responsible for closing
        it. If not provided, the client will create one.
    """

    def __init__(self, token: str, *, session: aiohttp.ClientSession | None = None) -> None:
        self.http = HTTPClient(token, session=session)

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the internal HTTP session."""

        await self.http.close()

    async def get_member_points(self, guild_id: int, member_id: int) -> GuildMemberPoints:
        """Get a guild member's points.

        Parameters
        ----------
        guild_id: :class:`int`
            The ID of the Discord guild.
        member_id: :class:`int`
            The ID of the Discord guild member.

        Returns
        -------
        :class:`GuildMemberPoints`
            The object holding the points information.
        """

        data = await self.http.get_guild_member_points(guild_id, member_id)
        return GUILD_MEMBER_POINTS_DECODER.decode(data)

    async def update_member_points(self, guild_id: int, member_id: int, amount: int) -> GuildMemberPoints:
        """Modify a guild member's points and return an updated version.

        Parameters
        ----------
        guild_id: :class:`int`
            The ID of the Discord guild.
        member_id: :class:`int`
            The ID of the Discord guild member.
        amount: :class:`int`
            The number of points to add or remove. Should not be 0 and cannot be more than 100,000 in either direction.

        Returns
        -------
        :class:`GuildMemberPoints`
            The object holding the updated points information.
        """

        if amount == 0 or abs(amount) > 100_000:
            msg = "Amount of points to add or remove cannot be 0 and cannot more than 100,000 in either direction."
            raise ValueError(msg)

        action = ActionType.REMOVE if amount < 0 else ActionType.ADD
        data = await self.http.modify_guild_member_points(guild_id, member_id, action.value, abs(amount))
        return GUILD_MEMBER_POINTS_DECODER.decode(data)

    async def update_member_score(self, guild_id: int, member_id: int, amount: int) -> GuildMemberScore:
        """Modify a guild member's score and return an updated version.

        Parameters
        ----------
        guild_id: :class:`int`
            The ID of the Discord guild.
        member_id: :class:`int`
            The ID of the Discord guild member.
        amount: :class:`int`
            The score to add or remove. Should not be 0 and cannot be more than 100,000 in either direction.

        Returns
        -------
        :class:`GuildMemberScore`
            The object holding the updated score information.
        """

        if amount == 0 or abs(amount) > 100_000:
            msg = "Score amount to add or remove cannot be 0 and cannot more than 100,000 in either direction."
            raise ValueError(msg)

        action = ActionType.REMOVE if amount < 0 else ActionType.ADD
        data = await self.http.modify_guild_member_score(guild_id, member_id, action.value, abs(amount))
        return GUILD_MEMBER_SCORE_DECODER.decode(data)

    async def get_member_ranking(
        self,
        guild_id: int,
        member_id: int,
        period: Literal["all", "month", "week"] = "all",
    ) -> GuildMemberRanking:
        """Get the ranking for a guild member over some period of time.

        Parameters
        ----------
        guild_id: :class:`int`
            The ID of the Discord guild.
        member_id: :class:`int`
            The ID of the Discord guild member.
        period: Literal["all", "month", "week"], default="all"
            The amount of time over which to consider the ranking, including all-time, last month, and last week.

        Returns
        -------
        :class:`GuildMemberRanking`
            The object holding the ranking information.
        """

        data = await self.http.get_guild_member_ranking(guild_id, member_id, period)
        return GUILD_MEMBER_RANKING_DECODER.decode(data)

    async def get_guild_rankings(
        self,
        guild_id: int,
        period: Literal["all", "month", "week"] = "all",
        *,
        start: int = 1,
        end: int | None = None,
    ) -> GuildRankings:
        """Get the rankings within a guild over some period of time.

        Parameters
        ----------
        guild_id: :class:`int`
            The ID of the Discord guild.
        period: Literal["all", "month", "week"], default="all"
            The amount of time over which to consider the ranking, including all-time, last month, and last week.
        start: :class:`int`, default=1
            The first rank to start searching from.
        end: :class:`int` | None, optional
            The last rank to retrieve. If not entered, API limit (per request) is automatically used - 100.

        Returns
        -------
        :class:`GuildRankings`
            The object holding a list of rankings.

        Raises
        ------
        ValueError
            If there's something wrong with the given start and end values.
        """

        # Check that start and end are valid.
        if start < 1:
            msg = "Start parameter must be greater than or equal to 1."
            raise ValueError(msg)
        if end:
            if end < 1:
                msg = "End parameter must be greater than or equal to 1."
                raise ValueError(msg)
            if end <= start:
                msg = "End must be greater than start if used."
                raise ValueError(msg)

        start -= 1  # Tatsu API is 0-indexed.

        # Just perform one request.
        if end is None:
            data = await self.http.get_guild_rankings(guild_id, period, offset=start)
            return GUILD_RANKINGS_DECODER.decode(data)

        end -= 1  # Tatsu API is 0-indexed.

        # Perform multiple requests if necessary and bring the rankings together in one object.
        coros = [self.http.get_guild_rankings(guild_id, period, offset=offset) for offset in range(start, end, 100)]
        results = await asyncio.gather(*coros)
        rankings_list = [GUILD_RANKINGS_DECODER.decode(result) for result in results]
        truncated_rankings = tuple(
            ranking
            for ranking in itertools.chain.from_iterable(item.rankings for item in rankings_list)
            if ranking.rank in range(start + 1, end + 2)
        )
        return GuildRankings(str(guild_id), truncated_rankings)

    async def get_user(self, user_id: int) -> User:
        """Get a user's profile.

        Parameters
        ----------
        user_id: :class:`int`
            The Discord ID of the user.

        Returns
        -------
        :class:`User`
            The user's profile.
        """

        data = await self.http.get_user_profile(user_id)
        return USER_DECODER.decode(data)

    async def get_store_listing(self, listing_id: str) -> StoreListing:
        """Get information about a listing from the Tatsu store.

        Parameters
        ----------
        listing_id: :class:`int`
            The ID of the store listing.

        Returns
        -------
        :class:`StoreListing`
            The store listing information.
        """

        data = await self.http.get_store_listing(listing_id)
        return STORE_LISTING_DECODER.decode(data)
