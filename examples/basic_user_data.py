import asyncio

import tatsu


async def main() -> None:
    """Get some basic information about a Discord member."""

    # To get your API key, use the command "t!apikey" on a server with Tatsu bot.
    api_key = "API_KEY"

    # The Discord ID of the official Tatsu server.
    test_guild = 173184118492889089

    # Random Discord user ID.
    test_user = 1234567891

    # The client can be used as a context manager to handle closing of the internal HTTP session.
    async with tatsu.Client(api_key) as client:
        profile: tatsu.User = await client.get_user(test_user)
        print(f"{profile.username} currently has {profile.credits} credits and {profile.reputation} reputation.")

        username = profile.username

        ranking: tatsu.GuildMemberRanking = await client.get_member_ranking(test_guild, test_user, "all")
        print(f"On the Tatsu server, {username} ranks at {ranking.rank} for all time.")

        before_points: tatsu.GuildMemberPoints = await client.get_member_points(test_guild, test_user)
        print(f"{username} - Points before update: {before_points.points}")

        after_points: tatsu.GuildMemberPoints = await client.update_member_points(test_guild, test_user, -10)
        print(f"{username} - Points after update: {after_points.points}")


asyncio.run(main())
