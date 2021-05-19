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

        
    @commands.command()
    async def embedtest123123(self, ctx):
        """embedtest123123"""
        botcolor = await ctx.embed_colour()
        e = discord.Embed(color=botcolor, description="desc")
        e.set_image(url="https://images-ext-2.discordapp.net/external/cC-YBJkH2GXnX7MHMASUM9Gle1S1im3rDJj2K54A28w/%3Fcid%3D73b8f7b19a5ccc575679c0a7fc4a673b753e4ce993f35223%26rid%3Dgiphy.mp4/https/media2.giphy.com/media/Q8bEDnj9hZd6vivXSZ/giphy.mp4")
        await ctx.send(embed=e)
