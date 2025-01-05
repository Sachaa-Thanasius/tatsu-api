"""
Tatsu API Wrapper
-----------------

A unofficial asynchronous wrapper for the Tatsu API.
"""

from __future__ import annotations

import enum
import logging
import sys
from collections.abc import AsyncGenerator
from datetime import datetime, timezone
from importlib.metadata import version as im_version
from typing import TYPE_CHECKING, Any, ClassVar, Literal, Optional, TypedDict
from urllib.parse import quote as uriquote

import aiohttp

from ._lockout import FIFOLockout


if sys.version_info >= (3, 11):
    from typing import NotRequired, Self
elif TYPE_CHECKING:
    from typing_extensions import NotRequired, Self
else:
    _GenericAlias = type(list[int])

    class _PlaceholderGenericAlias(_GenericAlias):
        def __repr__(self) -> str:
            return f"<import placeholder for {super().__repr__()}>"

    class _PlaceholderMeta(type):
        _source_module: str

        def __init__(self, *args: object, **kwargs: object) -> None:
            super().__init__(*args, **kwargs)
            self.__doc__ = f"Placeholder for {self._source_module}.{self.__name__}."

        def __repr__(self) -> str:
            return f"<import placeholder for {self._source_module}.{self.__name__}>"

    class _PlaceholderGenericMeta(_PlaceholderMeta):
        def __getitem__(self, item: object) -> _PlaceholderGenericAlias:
            return _PlaceholderGenericAlias(self, item)

    class NotRequired(metaclass=_PlaceholderGenericMeta):
        _source_module = "typing"

    class Self(metaclass=_PlaceholderMeta):
        _source_module = "typing"


__all__ = (
    # -- Exceptions
    "TatsuException",
    "HTTPException",
    "BadRequest",
    "Forbidden",
    "NotFound",
    "TatsuServerError",
    # -- Enums
    "ActionType",
    "SubscriptionType",
    "CurrencyType",
    # -- Models
    "GuildMemberPoints",
    "GuildMemberScore",
    "GuildMemberRanking",
    "Ranking",
    "GuildRankings",
    "User",
    "StorePrice",
    "StoreListing",
    # -- Client
    "Client",
)


_log = logging.getLogger(__name__)

_lockout_manager = FIFOLockout()

_MAX_GUILD_RANKINGS_PER_REQ = 100


# region -------- Exceptions --------


class TatsuException(Exception):
    """Base exception class for Tatsu."""


class HTTPException(TatsuException):
    """Exception that's raised when a non-200 HTTP status code is returned.

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

    response: aiohttp.ClientResponse
    status: int
    code: int
    text: str

    def __init__(self, response: aiohttp.ClientResponse, message: Optional[dict[str, Any]]) -> None:
        self.response = response
        self.status = response.status

        if message is not None:
            self.code = message.get("code", 0)
            self.text = message.get("message", "")
        else:
            self.code = 0
            self.text = ""

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


class TatsuServerError(HTTPException):
    """Exception that's raised when a 500 range status code occurs.

    Subclass of :exc:`HTTPException`.
    """


# endregion --------


# region -------- Enums --------


class ActionType(enum.IntEnum):
    """The way to modify a Tatsu user's score."""

    ADD = 0
    REMOVE = 1


class SubscriptionType(enum.Enum):
    """The type of Tatsu subscription a user has."""

    NONE = 0
    SUPPORTER1 = 1
    SUPPORTER2 = 2
    SUPPORTER3 = 3


class CurrencyType(enum.Enum):
    """A type of Tatsu currency."""

    CREDITS = 0
    TOKENS = 1
    EMERALDS = 2
    CANDY_CANE = 3
    USD = 4
    CANDY_CORN = 5


# endregion --------


# region -------- Payloads --------


class _GuildMemberPointsPayload(TypedDict):
    guild_id: str
    points: int
    rank: int
    user_id: str


class _GuildMemberScorePayload(TypedDict):
    guild_id: str
    score: int
    user_id: str


class _GuildMemberRankingPayload(TypedDict):
    guild_id: str
    rank: int
    score: int
    user_id: str


class _RankingPayload(TypedDict):
    rank: int
    score: int
    user_id: str


class _GuildRankingsPayload(TypedDict):
    guild_id: str
    rankings: list[_RankingPayload]


class _UserPayload(TypedDict):
    avatar_hash: str
    avatar_url: str
    credits: int
    discriminator: str
    id: str
    info_box: str
    reputation: int
    subscription_type: int
    subscription_renewal: NotRequired[str]  # ISO8601 timestamp
    title: str
    tokens: int
    username: str
    xp: int


class _StorePricePayload(TypedDict):
    currency: int
    amount: float


class _StoreListingPayload(TypedDict):
    id: str
    name: str
    summary: str
    description: str
    new: bool
    preview: NotRequired[str]
    prices: NotRequired[list[_StorePricePayload]]
    categories: NotRequired[list[str]]
    tags: NotRequired[list[str]]


# endregion --------


# region -------- Models --------


class GuildMemberPoints:
    """A Discord guild member's points information.

    Attributes
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

    __slots__ = ("guild_id", "points", "rank", "user_id")

    guild_id: str
    points: int
    rank: int
    user_id: str

    def __init__(self, guild_id: str, points: int, rank: int, user_id: str) -> None:
        self.guild_id = guild_id
        self.points = points
        self.rank = rank
        self.user_id = user_id

    @classmethod
    def _from_json(cls, payload: _GuildMemberPointsPayload) -> Self:
        return cls(payload["guild_id"], payload["points"], payload["rank"], payload["user_id"])

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(guild_id={self.guild_id}, points={self.points}, rank={self.rank}, user_id={self.user_id})"
        )


class GuildMemberScore:
    """A Discord guild member's score information.

    Attributes
    ----------
    guild_id: :class:`str`
        The Discord ID of the guild.
    score: :class:`int`
        The user's score.
    user_id: :class:`str`
        The user's Discord ID.
    """

    __slots__ = ("guild_id", "score", "user_id")

    guild_id: str
    score: int
    user_id: str

    def __init__(self, guild_id: str, score: int, user_id: str) -> None:
        self.guild_id = guild_id
        self.score = score
        self.user_id = user_id

    @classmethod
    def _from_json(cls, payload: _GuildMemberScorePayload) -> Self:
        return cls(payload["guild_id"], payload["score"], payload["user_id"])

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(guild_id={self.guild_id}, score={self.score}, user_id={self.user_id})"


class GuildMemberRanking:
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

    __slots__ = ("guild_id", "rank", "score", "user_id")

    guild_id: str
    rank: int
    score: int
    user_id: str

    def __init__(self, guild_id: str, rank: int, score: int, user_id: str) -> None:
        self.guild_id = guild_id
        self.rank = rank
        self.score = score
        self.user_id = user_id

    @classmethod
    def _from_json(cls, payload: _GuildMemberRankingPayload) -> Self:
        return cls(payload["guild_id"], payload["rank"], payload["score"], payload["user_id"])

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(guild_id={self.guild_id}, rank={self.rank}, score={self.score}, user_id={self.user_id})"
        )


class Ranking:
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

    __slots__ = ("rank", "score", "user_id")

    rank: int
    score: int
    user_id: str

    def __init__(self, rank: int, score: int, user_id: str) -> None:
        self.rank = rank
        self.score = score
        self.user_id = user_id

    @classmethod
    def _from_json(cls, payload: _RankingPayload) -> Self:
        return cls(payload["rank"], payload["score"], payload["user_id"])

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(rank={self.rank}, score={self.score}, user_id={self.user_id})"


class GuildRankings:
    """All the rankings in a guild over some period of time.

    Attributes
    ----------
    guild_id: :class:`str`
        The Discord ID of the guild.
    rankings: tuple[:class:`Ranking`, ...]
        The rankings.
    """

    __slots__ = ("guild_id", "rankings")

    guild_id: str
    rankings: tuple[Ranking, ...]

    def __init__(self, guild_id: str, rankings: tuple[Ranking, ...]) -> None:
        self.guild_id = guild_id
        self.rankings = rankings

    @classmethod
    def _from_json(cls, payload: _GuildRankingsPayload) -> Self:
        return cls(payload["guild_id"], tuple(map(Ranking._from_json, payload["rankings"])))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(guild_id={self.guild_id}, rankings={self.rankings!r})"


class User:
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
    subscription_renewal: :class:`datetime`, optional
        The subscription renewal time if the user has a subscription. Optional.
    title: class:`str`
        The text in the user's title.
    tokens: :class:`int`
        The amount of tokens the user has.
    username: class:`str`
        The user's Discord username.
    xp: :class:`int`
        The number of experience points the user has.
    """

    __slots__ = (
        "avatar_hash",
        "avatar_url",
        "credits",
        "discriminator",
        "id",
        "info_box",
        "reputation",
        "subscription_type",
        "title",
        "tokens",
        "username",
        "xp",
        "subscription_renewal",
    )

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
    subscription_renewal: Optional[datetime]

    def __init__(  # noqa: PLR0913
        self,
        avatar_hash: str,
        avatar_url: str,
        credits: int,  # noqa: A002
        discriminator: str,
        id: str,  # noqa: A002
        info_box: str,
        reputation: int,
        subscription_type: SubscriptionType,
        title: str,
        tokens: int,
        username: str,
        xp: int,
        subscription_renewal: Optional[datetime] = None,
    ) -> None:
        self.avatar_hash = avatar_hash
        self.avatar_url = avatar_url
        self.credits = credits
        self.discriminator = discriminator
        self.id = id
        self.info_box = info_box
        self.reputation = reputation
        self.subscription_type = subscription_type
        self.title = title
        self.tokens = tokens
        self.username = username
        self.xp = xp
        self.subscription_renewal = subscription_renewal

    @classmethod
    def _from_json(cls, payload: _UserPayload) -> Self:
        if (_raw_sub_renewal := payload.get("subscription_renewal")) is not None:
            # TODO: Double-check that this is fine.
            sub_renewal = datetime.strptime(_raw_sub_renewal, "%Y-%m-%dT%H:%M:%SZ")  # noqa: DTZ007
        else:
            sub_renewal = None

        return cls(
            payload["avatar_hash"],
            payload["avatar_url"],
            payload["credits"],
            payload["discriminator"],
            payload["id"],
            payload["info_box"],
            payload["reputation"],
            SubscriptionType(payload["subscription_type"]),
            payload["title"],
            payload["tokens"],
            payload["username"],
            payload["xp"],
            sub_renewal,
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({', '.join(f'{name}={getattr(self, name)}' for name in self.__slots__)})"


class StorePrice:
    """A price of a Tatsu store item.

    Attributes
    ----------
    currency: :class:`CurrencyType`
        The currency type.
    amount: :class:`float`
        The cost of the item in the currency.
    """

    __slots__ = ("currency", "amount")

    currency: CurrencyType
    amount: float

    def __init__(self, currency: CurrencyType, amount: float) -> None:
        self.currency = currency
        self.amount = amount

    @classmethod
    def _from_json(cls, payload: _StorePricePayload) -> Self:
        return cls(CurrencyType(payload["currency"]), payload["amount"])

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(currency={self.currency}, amount={self.amount})"


class StoreListing:
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
    new: :class:`str`
        Whether this is a new item in the store.
    preview: :class:`str`, optional
        The URL to an image preview of the item. Optional.
    prices: tuple[:class:`StorePrice`, ...], optional
        The prices for the item. Optional.
    categories: tuple[:class:`str`, ...], optional
        The categories for the item. Optional.
    tags: tuple[:class:`str`, ...], optional
        The tags for the item. Optional.
    """

    __slots__ = (
        "id",
        "name",
        "summary",
        "description",
        "new",
        "preview",
        "prices",
        "categories",
        "tags",
    )

    id: str
    name: str
    summary: str
    description: str
    new: bool
    preview: Optional[str]
    prices: tuple[StorePrice, ...]
    categories: tuple[str, ...]
    tags: tuple[str, ...]

    def __init__(  # noqa: PLR0913
        self,
        id: str,  # noqa: A002
        name: str,
        summary: str,
        description: str,
        new: bool,
        preview: Optional[str] = None,
        prices: tuple[StorePrice, ...] = (),
        categories: tuple[str, ...] = (),
        tags: tuple[str, ...] = (),
    ) -> None:
        self.id = id
        self.name = name
        self.summary = summary
        self.description = description
        self.new = new
        self.preview = preview
        self.prices = prices
        self.categories = categories
        self.tags = tags

    @classmethod
    def _from_json(cls, payload: _StoreListingPayload) -> Self:
        prices = tuple(map(StorePrice._from_json, payload.get("prices", ())))
        categories = tuple(payload.get("categories", ()))
        tags = tuple(payload.get("tags", ()))

        return cls(
            payload["id"],
            payload["name"],
            payload["summary"],
            payload["description"],
            payload["new"],
            payload.get("preview"),
            prices,
            categories,
            tags,
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({', '.join(f'{name}={getattr(self, name)}' for name in self.__slots__)})"


# endregion --------


# region -------- API client --------


class _Route:
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


class Client:
    """A client for interacting with the Tatsu API.

    Parameters
    ----------
    token: :class:`str`
        The Tatsu API key that will be used to authorize all requests to it.
    session: :class:`aiohttp.ClientSession`, optional
        A web client session to use for connecting to the API. If provided, the library is not responsible for closing
        it. If not provided, the client will create one.
    """

    def __init__(self, token: str, *, session: Optional[aiohttp.ClientSession] = None) -> None:
        self.token = token
        user_agent = "Tatsu (https://github.com/Sachaa-Thanasius/Tatsu {0} Python/{1[0]}.{1[1]} aiohttp/{2}"
        self.user_agent = user_agent.format(im_version("tatsu_api"), sys.version_info, im_version("aiohttp"))
        self._own_session = session is not None
        self._session = session

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        await self.close()

    async def _start_session(self) -> None:
        """Create an internal HTTP session for this client if necessary."""

        if (not self._session) or self._session.closed:
            self._session = aiohttp.ClientSession()
            self._own_session = True

    async def close(self) -> None:
        """Close the internal HTTP session."""

        if self._session and (not self._session.closed) and self._own_session:
            await self._session.close()

    async def _request(self, route: _Route, **kwargs: Any) -> Any:
        """Send an HTTP request to some endpoint in the Tatsu API.

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
        assert self._session is not None, "The session should always be initialized"

        response: Optional[aiohttp.ClientResponse] = None
        message: dict[str, Any] | None = None
        for _try in range(1, 6):
            async with _lockout_manager, self._session.request(route.method, route.url, **kwargs) as response:  # noqa: F811
                if _log.isEnabledFor(logging.DEBUG):
                    _log.debug("%s %s has returned %d.", route.method, response.url.human_repr(), response.status)

                resp_data = await response.json()

                rl_limit = int(response.headers.get("X-RateLimit-Limit", 1))
                rl_remaining = int(response.headers.get("X-RateLimit-Remaining", 0))
                rl_reset = float(response.headers["X-RateLimit-Reset"])

                rl_reset_dt = datetime.fromtimestamp(rl_reset, tz=timezone.utc).astimezone()

                _log.debug(
                    "Rate limit info: limit=%s, remaining=%s, reset=%s (try=%s)",
                    rl_limit,
                    rl_remaining,
                    rl_reset_dt,
                    _try,
                )

                # Preemptively sleep on the rate limit if "remaining" is 0 before a 429.
                if response.status != 429 and rl_remaining == 0:
                    now = datetime.now(tz=timezone.utc).astimezone()
                    rl_reset_after = (rl_reset_dt - now).total_seconds()
                    _log.warning("Emptied the rate limit early. Waiting for %s seconds for reset.", rl_reset_after)
                    _lockout_manager.lockout_for(rl_reset_after)

                # The request succeeded.
                if 300 > response.status >= 200:
                    _log.debug("%s %s has received %s", route.method, route.url, resp_data)
                    return resp_data

                # Sleep on the rate limit after a 429.
                if response.status == 429:
                    now = datetime.now(tz=timezone.utc).astimezone()
                    rl_reset_after = (rl_reset_dt - now).total_seconds()
                    _log.warning("Hit a rate limit. Waiting for %s seconds for reset.", rl_reset_after)
                    _lockout_manager.lockout_for(rl_reset_after)
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
            _log.debug("Reached maximum number of retries.")
            if response.status >= 500:
                raise TatsuServerError(response, message)
            raise HTTPException(response, message)

        msg = "Unreachable code in HTTP handling."
        raise RuntimeError(msg)

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

        route = _Route("GET", "/guilds/{guild_id}/members/{member_id}/points", guild_id=guild_id, member_id=member_id)
        response: _GuildMemberPointsPayload = await self._request(route)
        return GuildMemberPoints._from_json(response)

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

        Raises
        ------
        ValueError
            If the points amount is equal to 0 or greater than 100,000 in absolute value.
        """

        if amount == 0 or abs(amount) > 100_000:
            msg = "Amount of points to add or remove cannot be 0 and cannot more than 100,000 in either direction."
            raise ValueError(msg)

        action = ActionType.REMOVE if amount < 0 else ActionType.ADD
        route = _Route("PATCH", "/guilds/{guild_id}/members/{member_id}/points", guild_id=guild_id, member_id=member_id)
        json_data = {"action": action, "amount": amount}
        response: _GuildMemberPointsPayload = await self._request(route, json=json_data)
        return GuildMemberPoints._from_json(response)

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

        Raises
        ------
        ValueError
            If the score amount is equal to 0 or greater than 100,000 in absolute value.
        """

        if (amount == 0) or (abs(amount) > 100_000):
            msg = "Score amount to add or remove cannot be 0 and cannot more than 100,000 in either direction."
            raise ValueError(msg)

        action = ActionType.REMOVE if (amount < 0) else ActionType.ADD
        route = _Route("PATCH", "/guilds/{guild_id}/members/{member_id}/score", guild_id=guild_id, member_id=member_id)
        json_data = {"action": action, "amount": amount}
        response: _GuildMemberScorePayload = await self._request(route, json=json_data)
        return GuildMemberScore._from_json(response)

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

        route = _Route(
            "GET",
            "/guilds/{guild_id}/rankings/members/{user_id}/{time_range}",
            guild_id=guild_id,
            user_id=member_id,
            time_range=period,
        )
        response: _GuildMemberRankingPayload = await self._request(route)
        return GuildMemberRanking._from_json(response)

    async def guild_rankings(
        self,
        guild_id: int,
        period: Literal["all", "month", "week"] = "all",
        *,
        start: int = 1,
        end: Optional[int] = None,
    ) -> AsyncGenerator[Ranking]:
        """Return an asynchronous generator that iterates over the rankings in a guild over a period of time.

        Parameters
        ----------
        guild_id: :class:`int`
            The ID of the Discord guild.
        period: Literal["all", "month", "week"], default="all"
            The amount of time over which to consider the ranking, including all time, last month, and last week.
        start: :class:`int`, default=1
            The first rank to start searching from (inclusive).
        end: Optional[:class:`int`], optional
            The last rank to retrieve (inclusive). If not given, `start` + 100 is used, since 100 is the API limit
            (per request).

        Yields
        ------
        :class:`Ranking`
            A parsed ranking object.

        Raises
        ------
        ValueError
            If the given start and end values are not in the expected ranges.
        """

        if start < 1:
            msg = "Start parameter must be greater than or equal to 1."
            raise ValueError(msg)

        if end is not None:
            if end < 1:
                msg = "End parameter must be greater than or equal to 1."
                raise ValueError(msg)
            if end <= start:
                msg = "End must be greater than start."
                raise ValueError(msg)

        if end is None:
            end = start + _MAX_GUILD_RANKINGS_PER_REQ

        # Tatsu API is 0-indexed.
        start -= 1
        end -= 1

        route = _Route("GET", "/guilds/{guild_id}/rankings/{time_range}", guild_id=guild_id, time_range=period)

        # Paginate over the rankings in increments of 100.
        for offset in range(start, end, _MAX_GUILD_RANKINGS_PER_REQ):
            response: _GuildRankingsPayload = await self._request(route, params={"offset": offset})

            raw_rankings = response["rankings"]

            if (end - offset) < _MAX_GUILD_RANKINGS_PER_REQ:
                bounded_raw_rankings = raw_rankings[: end - offset]
            else:
                bounded_raw_rankings = raw_rankings

            for ranking in bounded_raw_rankings:
                yield Ranking._from_json(ranking)

            # No data is left after this iteration.
            if len(raw_rankings) < _MAX_GUILD_RANKINGS_PER_REQ:
                break

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

        route = _Route("GET", "/users/{user_id}/profile", user_id=user_id)
        response: _UserPayload = await self._request(route)
        return User._from_json(response)

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

        route = _Route("GET", "/store/listings/{listing_id}", listing_id=listing_id)
        response: _StoreListingPayload = await self._request(route)
        return StoreListing._from_json(response)


# endregion --------
