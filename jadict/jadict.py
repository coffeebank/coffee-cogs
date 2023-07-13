from redbot.core import Config, app_commands, commands, checks
from redbot.core.utils.views import SimpleMenu
import urllib.parse
import discord
import asyncio
import aiohttp
import json

from .jadict_utils import JadictUtils

class Jadict(commands.Cog):
    """Japanese dictionary bot. Searches Jisho using Jisho API."""

    def __init__(self, bot):
        self.config = Config.get_conf(self, identifier=806715409318936616)
        self.bot = bot

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
        total = len(jishoJson.get("data", []))

        for idx, jishoResult in enumerate(jishoJson.get("data", [])):
            if jishoResult.get("slug"):
                jisho_src = f"https://jisho.org/word/{jishoResult.get('slug')}"
            else:
                jisho_src = None

            kanji = jishoResult["japanese"][0].get("word", None)
            kana = jishoResult["japanese"][0].get("reading", None)
            word = kanji or kana

            if kanji and kana:
                # word == kanji -> show kana, romaji
                reading = kana+" "+JadictUtils.to_romaji(str(kana))
            else:
                # word == kana -> show only romaji
                reading = JadictUtils.to_romaji(str(word))

            is_common = None
            if jishoResult.get("is_common", None) is True:
                is_common = "Common"
            jlpt = None
            if len(jishoResult.get("jlpt", [])) > 0:
                jlpt = str(", ".join(jishoResult.get("jlpt", [])))
            tags = None
            if len(jishoResult.get("tags", [])) > 0:
                tags = str(", ".join(jishoResult.get("tags", [])))

            e = discord.Embed(
              color=(await self.bot.get_embed_colour(self)),
              title=str(word),
              url=jisho_src,
              description=" ・ ".join(filter(None, [reading, is_common, jlpt, tags]))
            )

            for index, sense in enumerate(jishoResult.get("senses", [])):
                parts_of_speech = str(", ".join(sense.get("parts_of_speech", [])))
                if len(parts_of_speech) > 0:
                    parts_of_speech = "*"+parts_of_speech+"*"
                english_definitions = str("; ".join(sense.get("english_definitions", [])))
                tags = ""
                if len(sense.get("tags", [])) > 0:
                    tags = "\n*Tags: " + str(", ".join(sense.get("tags", []))) + "*"
                see_also = ""
                if len(sense.get("see_also", [])) > 0:
                    see_also = "\n*See also: " + str(", ".join(sense.get("see_also", []))) + "*"
                links = ""
                if len(sense.get("links", [])) > 0:
                    links += "\n"
                    for sl in sense.get("links", []):
                        if sl.get("url") is not None:
                            links += f"[{sl.get('text', 'Link')}]({sl.get('url')}), "
                    links = links[:-2] # remove last comma and space

                e.add_field(
                    name=str(index+1)+". "+english_definitions, 
                    value=(parts_of_speech+tags+see_also+links or "-"),
                    inline=True
                )
            
            if jishoResult.get("attribution", None) is not None:
                attrs = ["Jisho API"]
                for k, v in jishoResult.get("attribution", {}).items():
                    if v is not False:
                        attrs.append(k)
                attr = "Results from "+", ".join(attrs)
                e.set_footer(text=attr+" ・ "+str(idx+1)+"/"+str(total))

            sendEmbeds.append({"embed": e})
        return sendEmbeds

    async def fallbackEmbed(self, ctx, rawText, footer=""):
        text = urllib.parse.quote(rawText, safe='')
        e = discord.Embed(color=(await self.bot.get_embed_colour(self)), title=rawText)
        e.add_field(name="Jisho", value=f"https://jisho.org/search/{text}")
        e.add_field(name="Wiktionary", value=f"https://en.wiktionary.org/w/index.php?fulltext=0&search={text}")
        e.add_field(name="DeepL Translate", value=f"https://deepl.com/translator#ja/en/{text}")
        e.add_field(name="Google Translate", value=f"https://translate.google.com/?text={text}")

        if footer:
            e.set_footer(text=footer)
        return e
  


    # Bot Commands

    @commands.hybrid_command(name="jadict", aliases=["jpdict", "jisho", "jishosearch"])
    @app_commands.describe(text="Search Japanese dictionary. By default, searches using Japanese and Romaji. When searching in English, please use  \"quotes\"")
    async def jadict(self, ctx, *, text):
        """Search Japanese dictionary

        Uses material from [Jisho](https://jisho.org), JMdict, JMnedict, DBpedia, and Wikipedia.
        
        By default, searches using Japanese and Romaji. When searching in English, please use  **`"quotes"`** .
        > ✅  東京, toukyou, or "tokyo"
        > ✅  らーめん, raamen, or "ramen"
        """
        jishoJson = await self.fetchJisho(text)

        if jishoJson is not False:
            sendEmbeds = await self.jishoEmbeds(ctx, jishoJson)
            await SimpleMenu(pages=sendEmbeds, timeout=90).start(ctx)
        elif jishoJson is False:
            fallback_embed = await self.fallbackEmbed(ctx, text, "No Jisho search results found. Please try other sources.")
            return await ctx.send(embed=fallback_embed)
        else:
            fallback_embed = await self.fallbackEmbed(ctx, text, "Could not connect to Jisho API")
            return await ctx.send(embed=fallback_embed)

    @commands.hybrid_command(name="jasearch", aliases=["jpsearch"])
    @app_commands.describe(text="Search Japanese vocabulary and translation websites")
    async def jasearch(self, ctx, *, text):
        """Search Japanese vocabulary and translation websites"""
        fallback_embed = await self.fallbackEmbed(ctx, text)
        return await ctx.send(embed=fallback_embed)
