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


    # Utility Commands

    async def fallbackEmbed(self, ctx, rawText, footer=""):
        text = urllib.parse.quote(rawText, safe='')
        deeplResult = await self.fetchDeepl(rawText)

        if deeplResult not in [False, None]:
            e = discord.Embed(color=(await ctx.embed_colour()), title=rawText, description=deeplResult)
        else:
            e = discord.Embed(color=(await ctx.embed_colour()), title=rawText)
        e.add_field(name="Krdict (한국어기초사전)", value=f"https://krdict.korean.go.kr/eng/dicSearch/search?nation=eng&nationCode=6&mainSearchWord={text}")
        e.add_field(name="Wiktionary", value=f"https://en.wiktionary.org/w/index.php?fulltext=0&search={text}")
        if deeplResult in [False, None]:
            e.add_field(name="DeepL Translate", value=f"https://deepl.com/translator#ko/en/{text}")
        e.add_field(name="Google Translate", value=f"https://translate.google.com/?text={text}")

        if footer:
            e.set_footer(text=footer)
        return e

    async def fetchDeepl(self, text):
        # Don't use pypi deepl: dependency conflict w/ idna; uses non-async requests
        deeplKeyObj = await self.bot.get_shared_api_tokens("deepl")
        deeplKey = deeplKeyObj.get("api_key")
        if deeplKey is None:
            print("Error: DeepL API key not set")
            return None
        try:
            deeplUrl = "https://api-free.deepl.com/v2/translate"
            payload = f"text={urllib.parse.quote(text, safe='')}&source_lang=EN&target_lang=KO"
            headers = {
                "Authorization": "DeepL-Auth-Key "+str(deeplKey),
                "Content-Type": "application/x-www-form-urlencoded"
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(deeplUrl, headers=headers, data=payload) as resp:
                    deeplJson = await resp.json()

                    # Check if it actually translated
                    try:
                        deepl_translated_text = deeplJson["translations"][0].get("text")
                        if text == deepl_translated_text:
                            # Deepl failed to translate properly
                            return False
                        return str(deepl_translated_text)
                    except:
                        return False
        except Exception as e:
            print(e)
            return None


    # Bot Commands

    @commands.hybrid_command(name="kodict", aliases=["krdict"])
    @app_commands.describe(text="Search Korean dictionary. Korean (Hangul/Hanja) supported.")
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

        # Fetch using Krdict API
        if krdictKey is not None:
            krResults = await krdictFetchApi(krdictKey, text)
        # Fetch using Krdict Scraper
        if krResults in [None, False]:
            krResults = await krdictFetchScraper(text)

        # Return data
        if krResults:
            sendEmbeds = await kodictEmbedKrdict(ctx, krResults)
            await SimpleMenu(pages=sendEmbeds, timeout=90).start(ctx)
        elif krResults is False:
            fallback_embed = await self.fallbackEmbed(ctx, text, "No Krdict search results found. Please try other sources.")
            return await ctx.send(embed=fallback_embed)
        else:
            fallback_embed = await self.fallbackEmbed(ctx, text, "Could not connect to Krdict API")
            return await ctx.send(embed=fallback_embed)

    @commands.hybrid_command(name="kosearch", aliases=["krsearch"])
    @app_commands.describe(text="Search Korean vocabulary and translation websites")
    async def kosearch(self, ctx, *, text):
        """Search Korean vocabulary and translation websites"""
        fallback_embed = await self.fallbackEmbed(ctx, text)
        return await ctx.send(embed=fallback_embed)
