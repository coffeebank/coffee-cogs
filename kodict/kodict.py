from redbot.core import Config, commands, checks
from redbot.core.utils.menus import menu, commands, DEFAULT_CONTROLS
import urllib.parse
import discord
import asyncio
import aiohttp
import defusedxml.ElementTree as ET
import json

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

    async def fetchKrdict(self, text):
        krdictKeyObj = await self.bot.get_shared_api_tokens("krdict")
        krdictKey = krdictKeyObj.get("api_key")
        if krdictKey is None:
            print("Error: Krdict API key not set")
            return None
        try:
            krdictUrl = f"https://krdict.korean.go.kr/api/search?key={krdictKey}&q={text}&translated=y&trans_lang=1"
            async with aiohttp.ClientSession() as session:
                # TODO: Consider using certifi in the future
                async with session.get(krdictUrl, ssl=False) as resp:
                    krdictXmlRaw = await resp.text()
                    krdictXml = ET.fromstring(krdictXmlRaw)

                    # Check if there are results
                    try:
                        krdictXml.findall("item")[0]
                        return krdictXml
                    except:
                        return False
        except Exception as e:
            print(e)
            return None

    async def kodictEmbeds(self, ctx, xmlTree):
        sendEmbeds = []

        attribution = "Results by 한국어기초사전"
        try:
            total = str(min(int(xmlTree.find("total").text), 10))+" results"
        except AttributeError:
            total = None

        for krResult in xmlTree.findall("item"):
            word = krResult.find("word").text
            link = krResult.find("link").text

            try:
                parts_of_speech = "` "+str(krResult.find("pos").text)+" `"
            except AttributeError:
                parts_of_speech = None
            try:
                origin = krResult.find("origin").text
            except AttributeError:
                origin = None
            try:
                pronunciation = krResult.find("pronunciation").text
            except AttributeError:
                pronunciation = None
            try:
                word_grade = "🏫 ` "+str(krResult.find("word_grade").text)+" `"
            except AttributeError:
                word_grade = None

            desc_body = " ・ ".join(filter(None, [pronunciation, origin, parts_of_speech, word_grade]))
            e = discord.Embed(color=(await ctx.embed_colour()), title=word, url=link, description=desc_body)

            for krrSense in krResult.findall("sense"):
                idx = krrSense.find("sense_order").text
                ko_def = krrSense.find("definition").text

                en_trans = krrSense.find("translation")
                en_word = en_trans.find("trans_word").text
                en_def = en_trans.find("trans_dfn").text

                e.add_field(
                  name=str(idx)+". "+en_word, 
                  value="\n".join([en_def, ko_def])
                )

            e.set_footer(text=" ・ ".join(filter(None, [attribution, total])))
            sendEmbeds.append(e)
        return sendEmbeds

    async def fallbackEmbed(self, ctx, rawText, footer=""):
        text = urllib.parse.quote(rawText, safe='')
        e = discord.Embed(color=(await ctx.embed_colour()), title=rawText)
        e.add_field(name="Krdict (한국어기초사전)", value=f"https://krdict.korean.go.kr/eng/dicSearch/search?nation=eng&nationCode=6&mainSearchWord={text}")
        e.add_field(name="Wiktionary", value=f"https://en.wiktionary.org/w/index.php?fulltext=0&search={text}")
        e.add_field(name="DeepL Translate", value=f"https://deepl.com/translator#ko/en/{text}")
        e.add_field(name="Google Translate", value=f"https://translate.google.com/?text={text}")

        if footer:
            e.set_footer(text=footer)
        return e
  


    # Bot Commands

    @commands.command(name="kodict", aliases=["krdict"])
    async def kodict(self, ctx, *, text):
        """Search Korean dictionary
        
        Uses the Krdict (한국어기초사전) Open API"""
        xmlTree = await self.fetchKrdict(text)

        if xmlTree is False:
            fallback_embed = await self.fallbackEmbed(ctx, text, "No Krdict search results found. Please try other sources.")
            return await ctx.send(embed=fallback_embed)
        elif xmlTree is not None:
            sendEmbeds = await self.kodictEmbeds(ctx, xmlTree)
            await menu(ctx, pages=sendEmbeds, controls=DEFAULT_CONTROLS, message=None, page=0, timeout=30)
        else:
            fallback_embed = await self.fallbackEmbed(ctx, text, "Could not connect to Krdict API")
            return await ctx.send(embed=fallback_embed)

    @commands.command(name="kosearch", aliases=["krsearch"])
    async def kosearch(self, ctx, *, text):
        """Search Korean vocabulary and translation websites"""
        fallback_embed = await self.fallbackEmbed(ctx, text)
        return await ctx.send(embed=fallback_embed)
