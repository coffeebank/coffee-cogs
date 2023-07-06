from redbot.core import Config, app_commands, commands, checks
import discord
import json
import urllib.parse

import aiohttp
import asyncio

from kodict.utils import *
from kodict.utils_deepl import *
from kodict.utils_discord import *
from kodict.utils_krdict import *
from kodict.redbot.core.utils.view import SimpleMenu

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
        # Respond early to prevent slash interaction from expiring
        response = await SimpleMenu(pages=[{'content': 'Searching...'}], timeout=90).start(ctx)
        try:
            embed_colour = await ctx.embed_colour()
        except Exception:
            pass

        krdict_key_obj = await self.bot.get_shared_api_tokens("krdict")
        krdict_key = krdict_key_obj.get("api_key", None)
        krdict_key_obj = await self.bot.get_shared_api_tokens("deepl")
        deepl_key = krdict_key_obj.get("api_key", None)
        results = await fetch_all(text, krdict_key, deepl_key)

        try:
            if results.get("krdict", None):
                attribution = ["Krdict (한국어기초사전)"]
                if results.get("deepl", None):
                    attribution.append("DeepL")
                send_embeds = await embed_krdict(results.get("krdict"), attribution, embed_colour)
                await SimpleMenu(pages=send_embeds, timeout=90).replace(ctx, response)
            elif results.get("deepl", None):
                deepl_embed = await embed_deepl(text, results.get("deepl"), None, embed_colour)
                await response.edit(content="", embed=deepl_embed)
            else:
                fallback_embed = await embed_fallback(text, None, "Could not connect to Krdict API", embed_colour)
                await response.edit(content="", embed=fallback_embed)
        except Exception:
            # User cancelled operation, ctx will return NotFound
            pass

    @commands.hybrid_command(name="kosearch", aliases=["krsearch"])
    @app_commands.describe(text="Search Korean vocabulary and translation websites")
    async def kosearch(self, ctx, *, text):
        """Search Korean vocabulary and translation websites"""
        fallback_embed = await embed_fallback(text)
        return await ctx.send(embed=fallback_embed)
