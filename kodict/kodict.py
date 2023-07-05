from redbot.core import Config, app_commands, commands, checks
import discord
import json
import urllib.parse

import aiohttp
import asyncio

from .kodict_utils import *
from kodict.redbot_core_utils_view import SimpleMenu

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
        loadframe = await SimpleMenu(pages=[{'content': 'Searching...'}], timeout=90).start(ctx)
        attribution = ["Krdict (한국어기초사전)"]
        try:
            embed_colour = await ctx.embed_colour()
        except Exception:
            pass

        # Attempt data fetch, but embedFallback if failed
        krdictKeyObj = await self.bot.get_shared_api_tokens("krdict")
        krdictKey = krdictKeyObj.get("api_key", None)
        krResults = None
        try:
            try:
                krResults = await fetchKrdict(text, krdictKey)
            except (ConnectionResetError, ClientConnectorError):
                # Connection failed, try again once more
                krResults = await fetchKrdict(text, krdictKey)
            # Krdict didn't return results, retry using DeepL
            if krResults in [None, False]:
                deeplKeyObj = await self.bot.get_shared_api_tokens("deepl")
                deeplKey = deeplKeyObj.get("api_key", None)
                deeplResult = await fetchDeepl(text, deeplKey)
                if deeplResult not in [None, False]:
                    attribution.append("DeepL")
                    krResults = await fetchKrdict(deeplResult, krdictKey)
        except Exception as err:
            print(err)
            pass

        # Return data
        try:
            if krResults:
                sendEmbeds = await embedKrdict(krResults, attribution, embed_colour)
                await SimpleMenu(pages=sendEmbeds, timeout=90).replace(ctx, loadframe)
            elif krResults is False:
                fallback_embed = await embedFallback(text, "No Krdict search results found. Please try other sources.", embed_colour)
                await ctx.send(embed=fallback_embed)
            else:
                fallback_embed = await embedFallback(text, "Could not connect to Krdict API", embed_colour)
                await ctx.send(embed=fallback_embed)
        except Exception:
            # User cancelled operation, ctx will return NotFound
            pass

    @commands.hybrid_command(name="kosearch", aliases=["krsearch"])
    @app_commands.describe(text="Search Korean vocabulary and translation websites")
    async def kosearch(self, ctx, *, text):
        """Search Korean vocabulary and translation websites"""
        fallback_embed = await embedFallback(ctx, text)
        return await ctx.send(embed=fallback_embed)
