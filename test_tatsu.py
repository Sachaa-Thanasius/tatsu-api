# TODO: Find a way to populate data necessary for these tests, e.g. user ids and guild ids, without making them public.

from __future__ import annotations

import asyncio
import json
from typing import Literal

import pytest
import pytest_asyncio

import tatsu_api as tatsu


# Make all the tests in this module run in the same event loop.
pytestmark = pytest.mark.asyncio(loop_scope="module")


# fmt: off
VALID_USER_ID = 158646501696864256              # Thanos
INVALID_USER_ID = 121212                        # Nonsense

VALID_GUILD_ID = 602735169090224139             # ACI
NONADMIN_MEMBER_GUILD_ID = 801834790768082944   # Panic
# fmt: on


@pytest_asyncio.fixture(scope="module")  # pyright: ignore [reportUnknownMemberType, reportUntypedFunctionDecorator]
async def client():
    with open("config.json") as fp:  # noqa: ASYNC230, PTH123
        api_key: str = json.load(fp)["API_KEY"]

    async with tatsu.Client(api_key) as client:
        yield client

    await asyncio.sleep(0.1)


@pytest.mark.parametrize("guild_id", [VALID_GUILD_ID, NONADMIN_MEMBER_GUILD_ID])
async def test_get_member_points_for_valid_user(client: tatsu.Client, guild_id: int):
    await client.get_member_points(guild_id, VALID_USER_ID)


async def test_get_member_points_for_invalid_user(client: tatsu.Client):
    # Can't know for sure which exception subclass this should raise or will in the future.
    with pytest.raises(tatsu.HTTPException):
        await client.get_member_points(VALID_GUILD_ID, INVALID_USER_ID)


async def test_update_member_points_as_admin(client: tatsu.Client):
    await client.update_member_points(VALID_GUILD_ID, VALID_USER_ID, -1)


async def test_update_member_score_as_admin(client: tatsu.Client):
    await client.update_member_score(VALID_GUILD_ID, VALID_USER_ID, -1)


async def test_update_member_score_in_nonadmin_guild(client: tatsu.Client):
    with pytest.raises(tatsu.Forbidden):
        await client.update_member_score(NONADMIN_MEMBER_GUILD_ID, VALID_USER_ID, -1)


@pytest.mark.parametrize("period", ["all", "month", "week"])
async def test_get_member_rankings(client: tatsu.Client, period: Literal["all", "month", "week"]):
    await client.get_member_ranking(VALID_GUILD_ID, VALID_USER_ID, period)


@pytest.mark.parametrize("period", ["all", "month", "week"])
async def test_get_guild_rankings_for_member_guild(client: tatsu.Client, period: Literal["all", "month", "week"]):
    rankings = [_ async for _ in client.guild_rankings(VALID_GUILD_ID, period, start=10, end=150)]
    assert len(rankings) > 0


@pytest.mark.parametrize(
    "guild_id",
    [
        pytest.param(302094807046684672, id="valid guild I've never been a member of"),
        pytest.param(123456, id="nonexistent guild"),
    ],
)
async def test_get_guild_rankings_for_invalid_guild(client: tatsu.Client, guild_id: int):
    with pytest.raises(tatsu.NotFound):
        [_ async for _ in client.guild_rankings(guild_id, "all")]


async def test_get_valid_user_profile(client: tatsu.Client):
    await client.get_user(VALID_USER_ID)


async def test_get_invalid_user_profile(client: tatsu.Client):
    with pytest.raises(tatsu.NotFound):
        await client.get_user(INVALID_USER_ID)


@pytest.mark.parametrize("listing_id", ["furni_1x1_antique_chair"])
async def test_get_valid_store_listing(client: tatsu.Client, listing_id: str):
    await client.get_store_listing(listing_id)


@pytest.mark.parametrize("listing_id", ["blahblah"])
async def test_get_invalid_store_listing(client: tatsu.Client, listing_id: str):
    with pytest.raises(tatsu.NotFound):
        await client.get_store_listing(listing_id)


# @pytest.mark.skip("Takes at least 1 minute to run")
async def test_lockout(client: tatsu.Client):
    # FIXME: The lockout doesn't work as used.
    # Either of the following occur:
    #   A) all requests go through within a few seconds, hammering the API.
    #   B) even after being handed a 429 or a remaining=0, a few more requests still go through before sleeping.
    # Is the lockout alone not the right primitive for this? Should I go back to the semaphore?

    import asyncio
    from itertools import chain

    coros = chain.from_iterable(
        (client.get_user(VALID_USER_ID), client.get_member_ranking(VALID_GUILD_ID, VALID_USER_ID, "all"))
        for _ in range(40)
    )

    _ = await asyncio.gather(*coros)
