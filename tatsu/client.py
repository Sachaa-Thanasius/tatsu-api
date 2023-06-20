"""
tatsu.client
------------

The client that serves as the user interface for the Tatsu API.
"""

from __future__ import annotations

import asyncio
import itertools
import logging
from typing import TYPE_CHECKING, Literal

import msgspec

from .enums import ActionType
from .http import HTTPClient
from .types_ import GuildMemberPoints, GuildMemberRanking, GuildMemberScore, GuildRankings, StoreListing, User

if TYPE_CHECKING:
    from types import TracebackType

    from typing_extensions import Self

__all__ = ("Client",)

_LOGGER = logging.getLogger(__name__)


class Client:
    """The client that is used to handle interaction with the Tatsu API.

    Parameters
    ----------
    token : :class:`str`
        The Tatsu API key that will be used to authorize all requests to it.

    Attributes
    ----------
    http : :class:`HTTPClient`
        The library's HTTP client for making requests to the Tatsu API. Initialized with the token.
    """

    def __init__(self, token: str) -> None:
        self.http = HTTPClient(token)

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type: type[BaseException], exc_val: BaseException, exc_tb: TracebackType) -> None:
        await self.close()

    async def close(self) -> None:
        """|coro|

        Close the internal HTTP session.
        """

        await self.http.close()

    async def get_member_points(self, guild_id: int, member_id: int) -> GuildMemberPoints:
        """|coro|

        Get a guild member's points.

        Parameters
        ----------
        guild_id : :class:`int`
            The ID of the Discord guild.
        member_id : :class:`int`
            The ID of the Discord guild member.

        Returns
        -------
        :class:`GuildMemberPoints`
            The object holding the points information.
        """

        data = await self.http.get_guild_member_points(guild_id, member_id)
        return msgspec.json.decode(data, type=GuildMemberPoints)

    async def update_member_points(self, guild_id: int, member_id: int, amount: int) -> GuildMemberPoints:
        """|coro|

        Modify a guild member's points and return an updated version.

        Parameters
        ----------
        guild_id : :class:`int`
            The ID of the Discord guild.
        member_id : :class:`int`
            The ID of the Discord guild member.
        amount : :class:`int`
            The number of points to add or remove.

        Returns
        -------
        :class:`GuildMemberPoints`
            The object holding the updated points information.
        """

        action = ActionType.REMOVE if amount < 0 else ActionType.ADD
        data = await self.http.modify_guild_member_points(guild_id, member_id, action, abs(amount))
        return msgspec.json.decode(data, type=GuildMemberPoints)

    async def update_member_score(self, guild_id: int, member_id: int, amount: int) -> GuildMemberScore:
        """|coro|

        Modify a guild member's score and return an updated version.

        Parameters
        ----------
        guild_id : :class:`int`
            The ID of the Discord guild.
        member_id : :class:`int`
            The ID of the Discord guild member.
        amount : :class:`int`
            The score number to add or remove.

        Returns
        -------
        :class:`GuildMemberScore`
            The object holding the updated score information.
        """

        action = ActionType.REMOVE if amount < 0 else ActionType.ADD
        data = await self.http.modify_guild_member_score(guild_id, member_id, action.value, abs(amount))
        return msgspec.json.decode(data, type=GuildMemberScore)

    async def get_member_ranking(
        self,
        guild_id: int,
        member_id: int,
        period: Literal["all", "month", "week"] = "all",
    ) -> GuildMemberRanking:
        """|coro|

        Get the ranking for a guild member over some period of time.

        Parameters
        ----------
        guild_id : :class:`int`
            The ID of the Discord guild.
        member_id : :class:`int`
            The ID of the Discord guild member.
        period : Literal["all", "month", "week"], default="all"
            The amount of time over which to consider the ranking, including all-time, last month, and last week.

        Returns
        -------
        :class:`GuildMemberRanking`
            The object holding the ranking information.
        """

        data = await self.http.get_guild_member_ranking(guild_id, member_id, period)
        return msgspec.json.decode(data, type=GuildMemberRanking)

    async def get_guild_rankings(
        self,
        guild_id: int,
        period: Literal["all", "month", "week"] = "all",
        *,
        start: int = 1,
        end: int | None = None,
    ) -> GuildRankings:
        """|coro|

        Get the rankings within a guild over some period of time.

        Parameters
        ----------
        guild_id : :class:`int`
            The ID of the Discord guild.
        period : Literal["all", "month", "week"], default="all"
            The amount of time over which to consider the ranking, including all-time, last month, and last week.
        start : :class:`int`, default=1
            The first rank to start searching from.
        end : :class:`int` | None, optional
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
            return msgspec.json.decode(data, type=GuildRankings)

        end -= 1  # Tatsu API is 0-indexed.

        # Perform multiple requests if necessary and bring the rankings together in one object.
        coros = [self.http.get_guild_rankings(guild_id, period, offset=offset) for offset in range(start, end, 100)]
        results = await asyncio.gather(*coros)
        rankings_list = [msgspec.json.decode(result, type=GuildRankings) for result in results]
        truncated_rankings = [
            ranking
            for ranking in itertools.chain(*[item.rankings for item in rankings_list])
            if ranking.rank in range(start + 1, end + 2)
        ]
        return GuildRankings(guild_id, truncated_rankings)

    async def get_user(self, user_id: int) -> User:
        """Get a user's profile.

        Parameters
        ----------
        user_id : :class:`int`
            The Discord ID of the user.

        Returns
        -------
        :class:`User`
            The user's profile.
        """

        data = await self.http.get_user_profile(user_id)
        return msgspec.json.decode(data, type=User)

    async def get_store_listing(self, listing_id: str) -> StoreListing:
        """Get information about a listing from the Tatsu store.

        Parameters
        ----------
        listing_id : :class:`int`
            The ID of the store listing.

        Returns
        -------
        :class:`StoreListing`
            The store listing information.
        """

        data = await self.http.get_store_listing(listing_id)
        return msgspec.json.decode(data, type=StoreListing)
