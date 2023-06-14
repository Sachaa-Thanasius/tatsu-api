# Tatsu
A lightweight and asynchronous wrapper for [Tatsu v1 API](https://tatsu.gg), written in Python. Supports every documented API endpoint.

Shoutout to the [discord.py](https://github.com/Rapptz/discord.py) wrapper for being an inspiration and providing a strong example for implementation.

*Note: Modifying a user's scores/points isn't possible without certain Discord permissions. See the API docs for more info.*

## Installing
Uploading to PyPI is being considered. For now, to install the library, run the following command:

```shell
# Linux/macOS
python3 -m pip install -U git+https://github.com/Sachaa-Thanasius/Tatsu

# Windows
py -3 -m pip install -U git+https://github.com/Sachaa-Thanasius/Tatsu
```

## Quick Example
```python
import asyncio
import tatsu

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