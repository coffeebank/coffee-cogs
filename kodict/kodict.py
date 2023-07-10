from redbot.core import Config, app_commands, commands
import discord

import aiohttp
import asyncio
import kodict_core

from .utils import *
from .coffee_redbot.core.utils.view import SimpleMenu

class Kodict(commands.Cog):
    """Korean dictionary bot. Searches National Institute of Korean Language's Korean-English Learners' Dictionary."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=806715409318936616)

    # This cog does not store any End User Data
    async def red_get_data_for_user(self, *, user_id: int):
        return {}
    async def red_delete_data_for_user(self, *, requester, user_id: int) -> None:
        pass


    # Bot Commands

    @commands.hybrid_command(name="kodict", aliases=["krdict"])
    @app_commands.describe(text="Search Korean dictionary. Search using Korean (Hangul/Hanja) and English.")
    async def kodict(self, ctx, *, text: str):
        """Search Korean dictionary
        
        Uses material by the [National Institute of Korean Language](https://korean.go.kr/), including [Krdict (한국어기초사전)](https://krdict.korean.go.kr/eng/).

        By default, searches using Korean (Hangul/Hanja) and English.
        > ✅  신문, 新聞, newspaper
        > ✅  만화, 漫畫, comics
        """
        embed_colour = await self.bot.get_embed_colour(self)
        krdict_key_obj = await self.bot.get_shared_api_tokens("krdict")
        deepl_key_obj = await self.bot.get_shared_api_tokens("deepl")
        await command_kodict(ctx, text, krdict_key_obj.get("api_key", None), deepl_key_obj.get("api_key", None), embed_colour)

    @commands.hybrid_command(name="kosearch", aliases=["krsearch"])
    @app_commands.describe(text="Search Korean vocabulary and translation websites")
    async def kosearch(self, ctx, *, text):
        """Search Korean vocabulary and translation websites"""
        fallback_embed = await embed_fallback(text)
        return await ctx.send(embed=fallback_embed)
