from __future__ import annotations

import asyncio
import functools
import json
import logging
import pathlib
from collections.abc import Callable, Coroutine
from typing import TYPE_CHECKING, Any, Literal, TypeVar

from test_logging import setup_logging

import tatsu


T = TypeVar("T")

if TYPE_CHECKING:
    from typing_extensions import ParamSpec

    P = ParamSpec("P")
else:
    P = TypeVar("P")


LOGGER = logging.getLogger(__name__)


def try_with_logging(func: Callable[P, Coroutine[Any, Any, T]]) -> Callable[P, Coroutine[Any, Any, T | None]]:
    """Utility decorator to wrap functions with a try-except-else and log the results."""

    @functools.wraps(func)
    async def wrapped(*args: P.args, **kwargs: P.kwargs) -> T | None:
        try:
            result = await func(*args, **kwargs)
        except Exception:
            LOGGER.exception("")
            return None
        else:
            LOGGER.info("%s\n", result)
            return result

    return wrapped


@try_with_logging
async def test_get_member_points(client: tatsu.Client, guild_id: int, user_id: int) -> tatsu.GuildMemberPoints:
    LOGGER.info("---Get member points.---")
    return await client.get_member_points(guild_id, user_id)


@try_with_logging
async def test_modify_member_points(
    client: tatsu.Client,
    guild_id: int,
    user_id: int,
    amount: int,
) -> tatsu.GuildMemberPoints:
    LOGGER.info("---Modify member points.---")
    return await client.update_member_points(guild_id, user_id, amount)


@try_with_logging
async def test_modify_member_score(
    client: tatsu.Client,
    guild_id: int,
    user_id: int,
    amount: int,
) -> tatsu.GuildMemberScore:
    LOGGER.info("---Modify member score.---")
    return await client.update_member_score(guild_id, user_id, amount)


@try_with_logging
async def test_get_member_rankings(
    client: tatsu.Client,
    guild_id: int,
    user_id: int,
    period: Literal["all", "month", "week"] = "all",
) -> tatsu.GuildMemberRanking:
    LOGGER.info("---Get member rankings.---")
    return await client.get_member_ranking(guild_id, user_id, period)


@try_with_logging
async def test_get_guild_rankings(
    client: tatsu.Client,
    guild_id: int,
    period: Literal["all", "month", "week"] = "all",
    *,
    start: int = 1,
    end: int | None = None,
) -> tatsu.GuildRankings:
    LOGGER.info("---Get guild rankings.---")
    return await client.get_guild_rankings(guild_id, period, start=start, end=end)


@try_with_logging
async def test_get_user_profile(client: tatsu.Client, user_id: int) -> tatsu.User:
    LOGGER.info("---Get user profile.---")
    return await client.get_user(user_id)


@try_with_logging
async def test_get_store_listing(client: tatsu.Client, listing_id: str) -> tatsu.StoreListing:
    LOGGER.info("---Get store listing.---")
    return await client.get_store_listing(listing_id)


async def main() -> None:
    """Test parts of the library."""

    setup_logging()

    with pathlib.Path(__file__).parents[1].joinpath("config.json").open(encoding="utf-8") as fp:
        config = json.load(fp)
    api_key: str = config["API_KEY"]

    wait_time = 2

    # Data to test with.
    my_user_id = 158646501696864256
    madeup_user_id = 121212

    aci_guild_id = 602735169090224139
    panic_guild_id = 801834790768082944
    not_in_guild_id = 302094807046684672
    madeup_guild_id = 10010

    actual_furniture_id = "furni_1x1_antique_chair"
    madeup_furniture_id = "a"

    async with tatsu.Client(api_key) as client:
        # Test every route.

        await test_get_guild_rankings(client, aci_guild_id, "all", start=114, end=250)
        await asyncio.sleep(wait_time)
        await test_get_guild_rankings(client, madeup_guild_id, "all")
        await asyncio.sleep(wait_time)
        await test_get_guild_rankings(client, not_in_guild_id, "all")
        await asyncio.sleep(wait_time)
        await test_get_user_profile(client, madeup_user_id)
        await asyncio.sleep(wait_time)
        await test_get_member_points(client, aci_guild_id, madeup_user_id)
        await asyncio.sleep(wait_time)
        await test_modify_member_score(client, aci_guild_id, my_user_id, 90_000)
        await asyncio.sleep(wait_time)
        await test_modify_member_score(client, aci_guild_id, my_user_id, -90_000)
        await asyncio.sleep(wait_time)
        await test_modify_member_score(client, panic_guild_id, my_user_id, 90_000)
        await asyncio.sleep(wait_time)

        for _ in range(27):
            await test_get_user_profile(client, my_user_id)
            await test_get_store_listing(client, actual_furniture_id)
            await test_get_store_listing(client, madeup_furniture_id)

        """
        for _ in range(18):
            await test_get_member_points(client, aci_guild_id, my_user_id)
            await test_modify_member_points(client, aci_guild_id, my_user_id, 1)
            await test_get_member_rankings(client, aci_guild_id, my_user_id, "all")
            await test_get_guild_rankings(client, aci_guild_id, "all")
            await test_get_user_profile(client, my_user_id)
        """

    LOGGER.info("Exiting...")
    await asyncio.sleep(0.1)


if __name__ == "__main__":
    asyncio.run(main())
