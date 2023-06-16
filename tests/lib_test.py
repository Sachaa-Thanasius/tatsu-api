import asyncio
import json
import logging
import pathlib
from typing import Literal

from test_logging import setup_logging

import tatsu

LOGGER = logging.getLogger(__name__)


async def test_get_member_points(client: tatsu.Client, guild_id: int, user_id: int) -> tatsu.GuildMemberPoints | None:
    LOGGER.info("---Get member points.---")
    try:
        result = await client.get_member_points(guild_id, user_id)
    except Exception as err:
        LOGGER.error("", exc_info=err)
        return None
    else:
        LOGGER.info("%s\n", result)
        return result


async def test_modify_member_points(
    client: tatsu.Client,
    guild_id: int,
    user_id: int,
    amount: int,
) -> tatsu.GuildMemberPoints | None:
    LOGGER.info("---Modify member points.---")
    try:
        result = await client.update_member_points(guild_id, user_id, amount)
    except Exception as err:
        LOGGER.error("", exc_info=err)
        return None
    else:
        LOGGER.info("%s\n", result)
        return result


async def test_modify_member_score(
    client: tatsu.Client,
    guild_id: int,
    user_id: int,
    amount: int,
) -> tatsu.GuildMemberScore | None:
    LOGGER.info("---Modify member score.---")
    try:
        result = await client.update_member_score(guild_id, user_id, amount)
    except Exception as err:
        LOGGER.error("", exc_info=err)
        return None
    else:
        LOGGER.info("%s\n", result)
        return result


async def test_get_member_rankings(
    client: tatsu.Client,
    guild_id: int,
    user_id: int,
    period: Literal["all", "month", "week"] = "all",
) -> tatsu.GuildMemberRanking | None:
    LOGGER.info("---Get member rankings.---")
    try:
        result = await client.get_member_ranking(guild_id, user_id, period)
    except Exception as err:
        LOGGER.error("", exc_info=err)
        return None
    else:
        LOGGER.info("%s\n", result)
        return result


async def test_get_guild_rankings(
    client: tatsu.Client,
    guild_id: int,
    period: Literal["all", "month", "week"] = "all",
    *,
    start: int = 1,
    end: int | None = None,
) -> tatsu.GuildRankings | None:
    LOGGER.info("---Get guild rankings.---")
    try:
        result = await client.get_guild_rankings(guild_id, period, start=start, end=end)
    except Exception as err:
        LOGGER.error("", exc_info=err)
        return None
    else:
        LOGGER.info("%s\n", result)
        return result


async def test_get_user_profile(client: tatsu.Client, user_id: int) -> tatsu.User | None:
    LOGGER.info("---Get user profile.---")
    try:
        result = await client.get_user(user_id)
    except Exception as err:
        LOGGER.error("", exc_info=err)
        return None
    else:
        LOGGER.info("%s\n", result)
        return result


async def test_get_store_listing(client: tatsu.Client, listing_id: str) -> tatsu.StoreListing | None:
    LOGGER.info("---Get store listing.---")
    try:
        result = await client.get_store_listing(listing_id)
    except Exception as err:
        LOGGER.error("", exc_info=err)
        return None
    else:
        LOGGER.info("%s\n", result)
        return result


async def main() -> None:
    """Test parts of the library."""

    setup_logging()
    with pathlib.Path(__file__).parents[1].joinpath("config.json").open(encoding="utf-8") as file:
        data = json.loads(file.read())
    api_key = data["API_KEY"]

    my_user_id = 158646501696864256
    aci_guild_id = 602735169090224139

    async with tatsu.Client(api_key) as client:
        # Test every route.
        """
        await test_get_guild_rankings(client, aci_guild_id, "all", start=114, end=250)
        await asyncio.sleep(wait_time)
        await test_get_guild_rankings(client, 10010, "all")
        await asyncio.sleep(wait_time)
        await test_get_guild_rankings(client, not_in_guild_id, "all")
        await asyncio.sleep(wait_time)
        await test_get_user_profile(client, 121212)
        await asyncio.sleep(wait_time)
        await test_get_member_points(client, aci_guild_id, 121212)
        await asyncio.sleep(wait_time)
        await test_modify_member_score(client, aci_guild_id, my_user_id, -90_000)
        await asyncio.sleep(wait_time)
        await test_modify_member_score(client, panic_guild_id, my_user_id, 90_000)
        await asyncio.sleep(wait_time)
        """
        await test_get_user_profile(client, my_user_id)
        await test_get_store_listing(client, "furni_1x1_antique_chair")
        await test_get_store_listing(client, "a")
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
