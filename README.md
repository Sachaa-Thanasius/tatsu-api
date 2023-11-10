# Tatsu API Wrapper
[![PyPI supported Python versions](https://img.shields.io/pypi/pyversions/tatsu-api.svg)](https://pypi.python.org/pypi/discord.py)
[![License: MIT](https://img.shields.io/github/license/Sachaa-Thanasius/tatsu-api.svg)](https://opensource.org/licenses/MIT)
[![Checked with pyright](https://img.shields.io/badge/pyright-checked-informational.svg)](https://github.com/microsoft/pyright/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)


A lightweight and asynchronous wrapper for [Tatsu v1 API](https://tatsu.gg), written in Python. Supports every documented API endpoint.

To get an API key, use the command "t!apikey" on a Discord server with the Tatsu bot present.

*Note: Modifying a user's scores/points isn't possible without certain Discord permissions. See the API docs for more info.*

## Installing

**tatsu-api currently requires Python 3.8 or higher.**

To install the library, run one of the following commands:

```shell
# Linux/macOS
python3 -m pip install -U tatsu-api

# Windows
py -3 -m pip install -U tatsu-api
```

## Quick Example
For more examples, see the [examples folder](./examples/).

```python
import asyncio
import tatsu_api as tatsu

async def main() -> None:
    """Example function."""
    
    api_key = "API_KEY"
    test_guild = 173184118492889089     # The Discord ID of the official Tatsu server.
    test_user = 1234567891              # Random Discord user ID.
    
    # The client can be used as a context manager to handle closing of the
    # internal HTTP session.
    async with tatsu.Client(api_key) as client:
        profile = await client.get_user(test_user)
        print(f"{profile.username} currently has {profile.credits} credits and {profile.reputation} reputation.")
        
        username = profile.username
        
        ranking = await client.get_member_ranking(test_guild, test_user, "all")
        print(f"On the Tatsu server, {username} ranks at {ranking.rank} for all time.")
        
        before_points = await client.get_member_points(test_guild, test_user)
        print(f"{username} - Points before update: {before_points.points}")
        
        after_points = await client.update_member_points(test_guild, test_user, -10)
        print(f"{username} - Points after update: {after_points.points}")

asyncio.run(main())
```

## Acknowledgements
Shoutout to [discord.py](https://github.com/Rapptz/discord.py) for being an inspiration and providing a strong example for implementation.