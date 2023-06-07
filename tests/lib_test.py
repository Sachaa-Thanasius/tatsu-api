import asyncio
import logging
from typing import Literal

from test_logging import setup_logging

import tatsu

LOGGER = logging.getLogger(__name__)


async def test_get_member_points(client: tatsu.Client, guild_id, user_id):
    LOGGER.info("---Get member points.---")
    try:
        result = await client.get_member_points(guild_id, user_id)
        LOGGER.info("%s\n", result)
        return result
    except Exception as err:
        LOGGER.error("", exc_info=err)


async def test_modify_member_points(client: tatsu.Client, guild_id: int, user_id: int, amount: int):
    LOGGER.info("---Modify member points.---")
    try:
        result = await client.update_member_points(guild_id, user_id, amount)
        LOGGER.info("%s\n", result)
        return result
    except Exception as err:
        LOGGER.error("", exc_info=err)


async def test_modify_member_score(client: tatsu.Client, guild_id: int, user_id: int, amount: int):
    LOGGER.info("---Modify member score.---")
    try:
        result = await client.update_member_score(guild_id, user_id, amount)
        LOGGER.info("%s\n", result)
        return result
    except Exception as err:
        LOGGER.error("", exc_info=err)


async def test_get_member_rankings(
        client: tatsu.Client,
        guild_id: int,
        user_id: int,
        period: Literal["all", "month", "week"] = "all",
):
    LOGGER.info("---Get member rankings.---")
    try:
        result = await client.get_member_ranking(guild_id, user_id, period)
        LOGGER.info("%s\n", result)
        return result
    except Exception as err:
        LOGGER.error("", exc_info=err)


async def test_get_guild_rankings(
        client: tatsu.Client,
        guild_id: int,
        period: Literal["all", "month", "week"] = "all",
        *,
        start: int = 1,
        end: int | None = None
):
    LOGGER.info("---Get guild rankings.---")
    try:
        result = await client.get_guild_rankings(guild_id, period, start=start, end=end)
        LOGGER.info("%s\n", result)
        return result
    except Exception as err:
        LOGGER.error("", exc_info=err)


async def test_get_user_profile(client: tatsu.Client, user_id: int):
    LOGGER.info("---Get user profile.---")
    try:
        result = await client.get_user(user_id)
        LOGGER.info("%s\n", result)
        return result
    except Exception as err:
        LOGGER.error("", exc_info=err)


async def main():
    """Test parts of the library."""

    setup_logging()

    token = "eUsBHScCkK-L5VVU4dDVMalFl069mwbTk"
    # test_user_id = 158646501696864256  # me
    test_guild_id = 602735169090224139  # ACI100

    async with tatsu.Client(token) as client:
        # Test every route.
        wait_time = 0.7
        await test_get_guild_rankings(client, test_guild_id, "all", start=114, end=250)
        await asyncio.sleep(wait_time)

        '''
        for _ in range(18):
            await test_get_member_points(client, test_guild_id, test_user_id)
            await asyncio.sleep(wait_time)
            # await test_modify_member_points(client, test_guild_id, test_user_id, 1)
            # await asyncio.sleep(wait_time)
            # await test_modify_member_score(client, test_guild_id, test_user_id, 1)
            # await asyncio.sleep(wait_time)
            await test_get_member_rankings(client, test_guild_id, test_user_id, "all")
            await asyncio.sleep(wait_time)
            await test_get_guild_rankings(client, test_guild_id, "all")
            await asyncio.sleep(wait_time)
            await test_get_user_profile(client, test_user_id)
            await asyncio.sleep(wait_time)
        '''

    print("Exiting...")
    await asyncio.sleep(0.5)


if __name__ == "__main__":
    asyncio.run(main())
