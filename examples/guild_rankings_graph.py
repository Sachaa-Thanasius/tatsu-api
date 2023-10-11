import asyncio

# You'll need to install these libraries to run this code. You can do so with pip.
import matplotlib.pyplot as plt
import numpy as np

import tatsu


async def main() -> None:
    """Create graphs that show the most active members on your Discord server over some period of time."""

    # To get your API key, use the command "t!apikey" on a server with Tatsu bot.
    api_key = "API_KEY"

    # Random Discord ID for a server that Tatsu bot is on.
    test_guild = 602735169090224139

    async with tatsu.Client(api_key) as client:
        base_title = "The Top 1000 Most Active Members of the Server"
        for coll_type in ("all", "month", "week"):
            # Get the data from the API.
            coll = await client.get_guild_rankings(test_guild, coll_type, end=1000)

            # Format the data with numpy.
            x = np.array([ranking.rank for ranking in coll.rankings])
            y = np.array([ranking.score for ranking in coll.rankings])

            raw_colors = np.array(["orange", "green", "blue"])
            length, leftover = np.divmod(len(coll.rankings), len(raw_colors))
            colors = np.concatenate((np.tile(raw_colors, length), np.array(raw_colors[:leftover])))

            # Plot the data with matplotlib.
            _, ax = plt.subplots()  # type: ignore
            ax.scatter(x, y, c=colors)
            ax.set_xlabel("Ranks")
            ax.set_ylabel("Scores")
            if coll_type == "all":
                ax.set_title(base_title + "\nof All Time")
            elif coll_type == "month":
                ax.set_title(base_title + "\nover the Last Month")
            else:
                ax.set_title(base_title + "\nover the Last Week")
            plt.show()  # type: ignore

    await asyncio.sleep(0.1)


asyncio.run(main())
