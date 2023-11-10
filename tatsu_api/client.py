from __future__ import annotations

import asyncio
import itertools
from typing import TYPE_CHECKING, Literal

import aiohttp

from .enums import ActionType
from .http import HTTPClient
from .models import (
    GUILD_MEMBER_POINTS_DECODER,
    GUILD_MEMBER_RANKING_DECODER,
    GUILD_MEMBER_SCORE_DECODER,
    GUILD_RANKINGS_DECODER,
    STORE_LISTING_DECODER,
    USER_DECODER,
    GuildMemberPoints,
    GuildMemberRanking,
    GuildMemberScore,
    GuildRankings,
    StoreListing,
    User,
)


if TYPE_CHECKING:
    from types import TracebackType

    from typing_extensions import Self
else:
    TracebackType = Self = object


__all__ = ("Client",)


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
