from redbot.core import Config, app_commands, commands, checks
from redbot.core.utils.views import SimpleMenu
import discord
import json
import urllib.parse

import aiohttp
import asyncio

from .kodict_utils import *

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
        krdictKeyObj = await self.bot.get_shared_api_tokens("krdict")
        krdictKey = krdictKeyObj.get("api_key", None)
        krResults = None
        attribution = ["Krdict (한국어기초사전)"]

        # Fetch using Krdict API
        if krdictKey is not None:
            krResults = await krdictFetchApi(krdictKey, text)
        # Fetch using Krdict Scraper
        if krResults in [None, False]:
            krResults = await krdictFetchScraper(text)

        # Fetch using DeepL + Krdict
        if krResults in [None, False]:
            deeplKeyObj = await self.bot.get_shared_api_tokens("deepl")
            deeplKey = deeplKeyObj.get("api_key", None)
            deeplResults = None
            if deeplKey is not None:
                deeplResults = await deeplFetchApi(deeplKey, text)
            if deeplResults not in [None, False]:
                attribution.append("DeepL")
                # Try again using Krdict API
                if krdictKey is not None:
                    krResults = await krdictFetchApi(krdictKey, deeplResults)
                # Try again using Krdict Scraper
                if krResults in [None, False]:
                    krResults = await krdictFetchScraper(deeplResults)

        # Return data
        if krResults:
            sendEmbeds = await embedKrdict(ctx, krResults, attribution)
            await SimpleMenu(pages=sendEmbeds, timeout=90).start(ctx)
        elif krResults is False:
            fallback_embed = await embedFallback(ctx, text, "No Krdict search results found. Please try other sources.")
            return await ctx.send(embed=fallback_embed)
        else:
            fallback_embed = await embedFallback(ctx, text, "Could not connect to Krdict API")
            return await ctx.send(embed=fallback_embed)

    @commands.hybrid_command(name="kosearch", aliases=["krsearch"])
    @app_commands.describe(text="Search Korean vocabulary and translation websites")
    async def kosearch(self, ctx, *, text):
        """Search Korean vocabulary and translation websites"""
        fallback_embed = await embedFallback(ctx, text)
        return await ctx.send(embed=fallback_embed)
