import json
from pathlib import Path
from redbot.core.bot import Red
from .loveping import loveping

async def setup(bot: Red) -> None:
    love_ping = loveping(bot)
    bot.add_cog(love_ping)
    await love_ping.initialize()
