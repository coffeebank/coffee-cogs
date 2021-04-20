from redbot.core import Config, commands, checks
from redbot.cogs.admin import admin
import asyncio
import aiohttp
import discord
from urllib.parse import quote
import json

class Coffeewip(commands.Cog):
    """General coffee-cogs wip commands"""

    def __init__(self):
        self.config = Config.get_conf(self, identifier=806715409318936616)
        default_guild = {
            "placeholder": 0
        }
        self.config.register_guild(**default_guild)

    async def red_get_data_for_user(self, *, user_id: int):
        # this cog does not story any data
        return {}

    async def red_delete_data_for_user(self, *, requester, user_id: int) -> None:
        # this cog does not story any data
        pass
