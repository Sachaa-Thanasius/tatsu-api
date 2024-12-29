from __future__ import annotations

import asyncio
import json
from typing import Literal

import pytest
import pytest_asyncio

import tatsu_api as tatsu


# TODO: Find a way to populate data necessary for these tests, e.g. user ids and guild ids, without making them public.


@pytest_asyncio.fixture(scope="module")  # pyright: ignore [reportUnknownMemberType, reportUntypedFunctionDecorator]
async def client():
    with open("config.json") as fp:  # noqa: ASYNC230, PTH123
        api_key: str = json.load(fp)["API_KEY"]

    async with tatsu.Client(api_key) as client:
        yield client

    await asyncio.sleep(0.1)


@pytest.mark.asyncio(loop_scope="module")
async def test_get_member_points_for_valid_user(client: tatsu.Client):
    valid_guild_id = 602735169090224139  # ACI
    valid_member_id = 158646501696864256  # Thanos

    await client.get_member_points(valid_guild_id, valid_member_id)


@pytest.mark.asyncio(loop_scope="module")
async def test_get_member_points_for_invalid_user(client: tatsu.Client):
    valid_guild_id = 602735169090224139  # ACI
    invalid_member_id = 121212

    # Can't know for sure which exception subclass this should raise or will in the future.
    with pytest.raises(tatsu.HTTPException):
        await client.get_member_points(valid_guild_id, invalid_member_id)


@pytest.mark.asyncio(loop_scope="module")
async def test_modify_member_points_as_admin(client: tatsu.Client):
    guild_id = 602735169090224139  # ACI
    guild_admin_id = 158646501696864256  # Thanos

    await client.update_member_points(guild_id, guild_admin_id, -1)


@pytest.mark.asyncio(loop_scope="module")
async def test_modify_member_score_as_admin(client: tatsu.Client):
    guild_id = 602735169090224139  # ACI
    guild_admin_id = 158646501696864256  # Thanos

    await client.update_member_score(guild_id, guild_admin_id, -1)


@pytest.mark.asyncio(loop_scope="module")
async def test_modify_member_score_in_nonadmin_guild(client: tatsu.Client):
    guild_id = 801834790768082944  # Panic
    guild_admin_id = 158646501696864256  # Thanos

    with pytest.raises(tatsu.Forbidden):
        await client.update_member_score(guild_id, guild_admin_id, -1)


@pytest.mark.parametrize("period", ["all", "month", "week"])
@pytest.mark.asyncio(loop_scope="module")
async def test_get_member_rankings(client: tatsu.Client, period: Literal["all", "month", "week"]):
    guild_id = 602735169090224139  # ACI
    member_id = 158646501696864256  # Thanos

    await client.get_member_ranking(guild_id, member_id, period)


@pytest.mark.parametrize("period", ["all", "month", "week"])
@pytest.mark.asyncio(loop_scope="module")
async def test_get_guild_rankings_for_member_guild(client: tatsu.Client, period: Literal["all", "month", "week"]):
    guild_id = 602735169090224139  # ACI

    await client.get_guild_rankings(guild_id, period, start=114, end=250)


@pytest.mark.parametrize(
    "guild_id",
    [
        pytest.param(302094807046684672, id="valid guild I'm not a member of"),
        pytest.param(123456, id="nonexistent guild"),
    ],
)
@pytest.mark.asyncio(loop_scope="module")
async def test_get_guild_rankings_for_invalid_guild(client: tatsu.Client, guild_id: int):
    # Can't know for sure which exception subclass this should raise or will in the future.
    with pytest.raises(tatsu.HTTPException):
        await client.get_guild_rankings(guild_id, "all")


@pytest.mark.asyncio(loop_scope="module")
async def test_get_valid_user_profile(client: tatsu.Client):
    valid_user_id = 158646501696864256  # Thanos
    await client.get_user(valid_user_id)


@pytest.mark.asyncio(loop_scope="module")
async def test_get_invalid_user_profile(client: tatsu.Client):
    invalid_user_id = 121212

    # Can't know for sure which exception subclass this should raise or will in the future.
    with pytest.raises(tatsu.HTTPException):
        await client.get_user(invalid_user_id)


@pytest.mark.parametrize("listing_id", ["furni_1x1_antique_chair"])
@pytest.mark.asyncio(loop_scope="module")
async def test_get_valid_store_listing(client: tatsu.Client, listing_id: str):
    await client.get_store_listing(listing_id)


@pytest.mark.parametrize("listing_id", ["blahblah"])
@pytest.mark.asyncio(loop_scope="module")
async def test_get_invalid_store_listing(client: tatsu.Client, listing_id: str):
    # Can't know for sure which exception subclass this should raise or will in the future.
    with pytest.raises(tatsu.HTTPException):
        await client.get_store_listing(listing_id)
