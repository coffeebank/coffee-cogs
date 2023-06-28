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
            krdictUrl = f"https://krdict.korean.go.kr/api/search?key={krdictKey}&q={urllib.parse.quote(text, safe='')}&translated=y&trans_lang=1"
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

    def koPos(self, text):
        parts_of_speech_blocks = {
          "형용사": "Adjective",
          "부사": "Adverb",
          "감탄사": "Interjection",
          "명사": "Noun",
          "접사": "Prefix/Suffix",
          "어미": "Suffix",
          "동사": "Verb",
        }
        return parts_of_speech_blocks.get(text, None)

    def koWordGrade(self, text):
        word_grade_blocks = {
          "초급": "Beginner",
          "중급": "Intermediate",
          "고급": "Advanced",
        }
        return word_grade_blocks.get(text, None)

    async def kodictEmbeds(self, ctx, xmlTree):
        sendEmbeds = []

        attribution = "Results from Krdict (한국어기초사전)"
        try:
            total = str(min(int(xmlTree.find("total").text), 10))
        except AttributeError:
            total = None

        for resIdx, krResult in enumerate(xmlTree.findall("item")):
            word = str(krResult.find("word").text)
            link = str(krResult.find("link").text)

            parts_of_speech = None
            try:
                pos_none = ["품사 없음"]
                if krResult.find("pos").text and (krResult.find("pos").text not in pos_none):
                    parts_of_speech_raw = str(krResult.find("pos").text)
                    level_gauge = self.koPos(parts_of_speech_raw)
                    parts_of_speech = "` "+" ".join(filter(None, [parts_of_speech_raw, level_gauge]))+" `"
            except AttributeError:
                pass

            try:
                origin = str(krResult.find("origin").text)
            except AttributeError:
                origin = None
            try:
                pronunciation = str(krResult.find("pronunciation").text)
            except AttributeError:
                pronunciation = None
            try:
                word_grade_raw = str(krResult.find("word_grade").text)
                level_gauge = self.koWordGrade(word_grade_raw)
                word_grade = "` "+" ".join(filter(None, [word_grade_raw, level_gauge]))+" `"
            except AttributeError:
                word_grade = None

            desc_body = " ・ ".join(filter(None, [pronunciation, origin, parts_of_speech, word_grade]))
            e = discord.Embed(color=(await ctx.embed_colour()), title=word, url=link, description=desc_body)

            for idx, krrSense in enumerate(krResult.findall("sense")):
                try:
                    senseIdx = str(krrSense.find("sense_order").text)
                except AttributeError:
                    senseIdx = idx+1 
                try:
                    ko_def = str(krrSense.find("definition").text)
                except AttributeError:
                    ko_def = None

                try:
                    en_trans = krrSense.find("translation")
                    en_word = str(en_trans.find("trans_word").text)
                    en_def = str(en_trans.find("trans_dfn").text)
                except AttributeError:
                    en_trans = None
                    en_word = ""
                    en_def = f"[See translation on DeepL](https://www.deepl.com/translator#ko/en/{urllib.parse.quote(ko_def, safe='')})"

                e.add_field(
                  name=str(senseIdx)+". "+str(en_word), 
                  value="\n".join(filter(None, [en_def, ko_def]))
                )

            e.set_footer(text=" ・ ".join(filter(None, [str(attribution), str(resIdx+1)+"/"+str(total)])))
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
        
        Uses the Krdict (한국어기초사전) Open API

        Currently, only searching in Korean is supported.
        - Korean Hanja is variant-sensitive (must be in Korean, not Chinese/Japanese)
        - Searching in English is not yet supported"""
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
