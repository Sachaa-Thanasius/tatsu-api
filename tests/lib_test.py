import asyncio
import logging
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
    else:
        LOGGER.info("%s\n", result)
        return result


async def test_modify_member_score(
        client: tatsu.Client,
        guild_id: int,
        user_id: int,
        amount: int
) -> tatsu.GuildMemberScore | None:
    LOGGER.info("---Modify member score.---")
    try:
        result = await client.update_member_score(guild_id, user_id, amount)
    except Exception as err:
        LOGGER.error("", exc_info=err)
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
    else:
        LOGGER.info("%s\n", result)
        return result


async def test_get_user_profile(client: tatsu.Client, user_id: int) -> tatsu.User:
    LOGGER.info("---Get user profile.---")
    try:
        result = await client.get_user(user_id)
    except Exception as err:
        LOGGER.error("", exc_info=err)
    else:
        LOGGER.info("%s\n", result)
        return result


async def main() -> None:
    """Test parts of the library."""

    setup_logging()

    token = "eUsBHScCkK-L5VVU4dDVMalFl069mwbTk"
    my_user_id = 158646501696864256  # me
    aci_guild_id = 602735169090224139  # ACI100
    panic_guild_id = 801834790768082944
    not_in_guild_id = 974519864045756446

    async with tatsu.Client(token) as client:
        # Test every route.
        wait_time = 0.7
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

        for _ in range(18):
            await test_get_member_points(client, aci_guild_id, my_user_id)
            # await test_modify_member_points(client, aci_guild_id, my_user_id, 1)
            # await asyncio.sleep(wait_time)
            # await test_modify_member_score(client, aci_guild_id, my_user_id, 1)
            # await asyncio.sleep(wait_time)
            await test_get_member_rankings(client, aci_guild_id, my_user_id, "all")
            await test_get_guild_rankings(client, aci_guild_id, "all")
            await test_get_user_profile(client, my_user_id)

    LOGGER.info("Exiting...")
    await asyncio.sleep(0.5)


if __name__ == "__main__":
    asyncio.run(main())
