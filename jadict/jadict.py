from redbot.core import Config, commands, checks
from redbot.core.utils.menus import menu, commands, DEFAULT_CONTROLS
import urllib.parse
import discord
import asyncio
import aiohttp
import json

class Jadict(commands.Cog):
    """Japanese dictionary bot. Searches Jisho using Jisho API."""

    def __init__(self):
        self.config = Config.get_conf(self, identifier=806715409318936616)

    # This cog does not store any End User Data
    async def red_get_data_for_user(self, *, user_id: int):
        return {}
    async def red_delete_data_for_user(self, *, requester, user_id: int) -> None:
        pass


    # Utility Commands

    async def makeJsonRequest(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                reqdata = await resp.json()
                return reqdata

    async def fetchJisho(self, text):
        try:
            jishoJson = await self.makeJsonRequest(f"http://jisho.org/api/v1/search/words?keyword={text}")
            if len(jishoJson.get("data", [])) > 0:
                return jishoJson
            else:
                return False
        except:
            return None
        
    async def jishoEmbeds(self, ctx, jishoJson):
        sendEmbeds = []
        for jishoResult in jishoJson.get("data", []):
            kanji = str(jishoResult["japanese"][0].get("word", None))
            reading = str(jishoResult["japanese"][0].get("reading", None))
            is_common = ""
            if jishoResult.get("is_common", None) is True:
                is_common = " ・ Common"
            tags = ""
            if len(jishoResult.get("jlpt", [])) > 0:
                tags += " ・ "+str(", ".join(jishoResult.get("jlpt", [])))
            if len(jishoResult.get("tags", [])) > 0:
                tags += " ・ "+str(", ".join(jishoResult.get("tags", [])))

            if kanji != "None":
                e = discord.Embed(color=(await ctx.embed_colour()), title=kanji, description=reading+is_common+tags)
            else:
                e = discord.Embed(color=(await ctx.embed_colour()), title=reading, description=is_common+tags)

            for index, sense in enumerate(jishoResult.get("senses", [])):
                parts_of_speech = str(", ".join(sense.get("parts_of_speech", [])))
                english_definitions = str("; ".join(sense.get("english_definitions", [])))
                tags = ""
                if len(sense.get("tags", [])) > 0:
                    tags = "\n*Tags: " + str(", ".join(sense.get("tags", []))) + "*"
                see_also = ""
                if len(sense.get("see_also", [])) > 0:
                    see_also = "\n*See also: " + str(", ".join(sense.get("see_also", []))) + "*"

                e.add_field(
                    name=str(index+1)+". "+english_definitions, 
                    value="*"+parts_of_speech+"*"+tags+see_also,
                    inline=True
                )
            
            if jishoResult.get("attribution", None) is not None:
                attrs = ["Jisho API"]
                for k, v in jishoResult.get("attribution", {}).items():
                    if v is not False:
                        attrs.append(k)
                attr = "Results from "+", ".join(attrs)
                e.set_footer(text=attr)

            sendEmbeds.append(e)
        return sendEmbeds

    async def fallbackEmbed(self, ctx, rawText, footer=""):
        text = urllib.parse.quote(rawText, safe='')
        e = discord.Embed(color=(await ctx.embed_colour()), title=rawText)
        e.add_field(name="Jisho", value=f"https://jisho.org/search/{text}")
        e.add_field(name="Wiktionary", value=f"https://en.wiktionary.org/w/index.php?fulltext=0&search={text}")
        e.add_field(name="DeepL Translate", value=f"https://deepl.com/translator#ja/en/{text}")
        e.add_field(name="Google Translate", value=f"https://translate.google.com/?text={text}")

        if footer:
            e.set_footer(text=footer)
        return e
  


    # Bot Commands

    @commands.command(name="jishosearch", aliases=["jisho"])
    async def jishosearch(self, ctx, *, text):
        """Search Japanese dictionary
        
        By default, searches Jisho using Japanese and Romaji. When searching in English, please use  **`"quotes"`** .

        > ✅  東京, toukyou, or "tokyo"
        > ❌  tokyo
        """
        jishoJson = await self.fetchJisho(text)

        if jishoJson is not False:
            sendEmbeds = await self.jishoEmbeds(ctx, jishoJson)
            await menu(ctx, pages=sendEmbeds, controls=DEFAULT_CONTROLS, message=None, page=0, timeout=30)
        elif jishoJson is False:
            fallback_embed = await self.fallbackEmbed(ctx, text, "No Jisho search results found. Please try other sources.")
            return await ctx.send(embed=fallback_embed)
        else:
            fallback_embed = await self.fallbackEmbed(ctx, text, "Could not connect to Jisho API")
            return await ctx.send(embed=fallback_embed)

    @commands.command(name="jasearch", aliases=["jpsearch"])
    async def jasearch(self, ctx, *, text):
        """Search Japanese vocabulary and translation websites"""
        fallback_embed = await self.fallbackEmbed(ctx, text)
        return await ctx.send(embed=fallback_embed)
