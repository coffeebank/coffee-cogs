from redbot.core import Config, commands, checks
from redbot.cogs.admin import admin
from array import *
import asyncio
import aiohttp
import discord
from urllib.parse import quote
import random

class google(commands.Cog):
    """Gives you links to common search engines based on a search query."""

    def __init__(self):
        self.config = Config.get_conf(self, identifier=806715409318936616)
        default_guild = {
            "searchEngines": [
                "Google: https://www.google.com/search?hl=en&q=",
                "Bing: https://www.bing.com/search?q=",
                "DuckDuckGo: https://duckduckgo.com/?t=ffab&q="
            ]
        }
        self.config.register_guild(**default_guild)

    async def red_get_data_for_user(self, *, user_id: int):
        # this cog does not story any data
        return {}

    async def red_delete_data_for_user(self, *, requester, user_id: int) -> None:
        # this cog does not story any data
        pass

    @commands.command()
    async def google(self, ctx, *, searchtext):
        if searchtext:
            query = quote(searchtext)
            searchEngines = await self.config.guild(ctx.guild).searchEngines()
            message = ""
            
            for k in searchEngines:
                message = message + "\n" + k + query

            await ctx.send(message)
