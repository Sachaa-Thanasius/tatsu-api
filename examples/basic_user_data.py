import asyncio

import tatsu_api as tatsu


async def main() -> None:
    """Get some basic information about a Discord member."""

    # To get your API key, use the command "t!apikey" on a server with Tatsu bot.
    api_key = "API_KEY"

    # The Discord ID of the official Tatsu server.
    test_guild = 173184118492889089

    # Random Discord user ID.
    test_user = 1234567890

    # The client can be used as a context manager to handle closing of the internal HTTP session.
    async with tatsu.Client(api_key) as client:
        profile = await client.get_user(test_user)
        print(f"{profile.username} currently has {profile.credits} credits and {profile.reputation} reputation.")

        username = profile.username

        ranking = await client.get_member_ranking(test_guild, test_user, "all")
        print(f"On this server, {username} ranks at {ranking.rank} for all time.")

        before_points = await client.get_member_points(test_guild, test_user)
        print(f"{username} - Current points: {before_points.points}")


if __name__ == "__main__":
    asyncio.run(main())
