from redbot.core import Config, commands, checks
from redbot.cogs.admin import admin
from array import *
# from dhooks import Webhook, Embed # Keeping for the future
import asyncio
import aiohttp
import discord
import time
import random

class quarantine(commands.Cog):
    """Quarantine a user"""

    def __init__(self):
        self.config = Config.get_conf(self, identifier=760098403388227625)
        default_guild = {
            "muterole": "782383728634101781"
        }
        self.config.register_guild(**default_guild)

    async def red_get_data_for_user(self, *, user_id: int):
        # this cog does not story any data
        return {}

    async def red_delete_data_for_user(self, *, requester, user_id: int) -> None:
        # this cog does not story any data
        pass

    @commands.command()
    @checks.mod()
    async def nsfw(self, ctx, *, user: discord.Member=None):
        if not user:
            await ctx.send("no user specified")
        else:
            role = await self.config.guild(ctx.guild).muterole()
            admin._addrole(self, ctx, user, role)
            # await self.add_roles(user, role)
            # await ctx.send("hello " + user.mention + ", you now have the role <@&" + role + ">")
