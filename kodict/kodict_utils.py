import discord
import urllib.parse

import aiohttp
import asyncio
from korean_romanizer.romanizer import Romanizer
import krdict
import lxml

parts_of_speech_blocks = {
  "명사": "Noun",
  "대명사": "Pronoun",
  "수사": "Number",
  "조사": "Particle",
  "동사": "Verb",
  "형용사": "Adjective",
  "관형사": "Modifier",
  "부사": "Adverb",
  "감탄사": "Interjection",
  "접사": "Prefix/Suffix",
  "의존 명사": "Dependent Noun",
  "보조 동사": "Auxiliary Verb",
  "보조 형용사": "Auxiliary Adjective",
  "어미": "Suffix",
}

word_grade_blocks = {
  "초급": "Beginner",
  "중급": "Intermediate",
  "고급": "Advanced",
}

async def kodictEmbedKrdict(ctx, krdict_results):
    sendEmbeds = []
    attribution = "Results from Krdict (한국어기초사전)"
    try:
        total = str(min(int(krdict_results.total_results), 10))
    except:
        total = "..."

    for resIdx, krResult in enumerate(krdict_results.results):
        word = str(krResult.word)
        link = str(krResult.url)

        try:
            pronunciation_kr = str(krResult.pronunciation)
        except AttributeError:
            pronunciation_kr = None
        try:
            romanization = str(Romanizer(str(word)).romanize())
        except:
            romanization = None
        pronunciation = " ".join(filter(None, [pronunciation_kr, romanization]))
        
        try:
            origin = str(krResult.origin)
        except AttributeError:
            origin = None

        parts_of_speech = None
        try:
            if krResult.part_of_speech and (krResult.part_of_speech not in ["품사 없음", "None", None]):
                parts_of_speech_raw = str(krResult.part_of_speech)
                eng_pos = str(parts_of_speech_blocks.get(parts_of_speech_raw, None))
                parts_of_speech = "` "+" ".join(filter(None, [parts_of_speech_raw, eng_pos]))+" `"
        except AttributeError:
            pass

        word_grade = None
        try:
            if krResult.vocabulary_level and (krResult.vocabulary_level not in ["None", None]):
                word_grade_raw = str(krResult.vocabulary_level)
                level_gauge = str(word_grade_blocks.get(word_grade_raw, None))
                word_grade = "` "+" ".join(filter(None, [word_grade_raw, level_gauge]))+" `"
        except AttributeError:
            pass

        desc_body = " ・ ".join(filter(None, [pronunciation, origin, parts_of_speech, word_grade]))
        e = discord.Embed(color=(await ctx.embed_colour()), title=word, url=link, description=desc_body)

        for idx, krrSense in enumerate(krResult.definitions):
            try:
                senseIdx = str(krrSense.order)
            except AttributeError:
                senseIdx = idx+1 
            try:
                ko_def = str(krrSense.definition)
            except AttributeError:
                ko_def = None

            try:
                en_trans = krrSense.translations[0]
                en_word = str(en_trans.word)
                en_def = str(en_trans.definition)
            except (AttributeError, IndexError) as err:
                en_trans = None
                en_word = ""
                en_def = f"[See translation on DeepL](https://www.deepl.com/translator#ko/en/{urllib.parse.quote(str(ko_def), safe='')})"

            e.add_field(
              name=str(senseIdx)+". "+str(en_word), 
              value="\n".join(filter(None, [en_def, ko_def]))
            )

        e.set_footer(text=" ・ ".join(filter(None, [str(attribution), str(resIdx+1)+"/"+str(total)])))
        sendEmbeds.append({"embed": e})
    return sendEmbeds

async def krdictFetchApi(api_key: str, text: str):
    krdict.set_key(api_key)
    response = krdict.search(query=text, translation_language="english", raise_api_errors=True)
    return krdictFetchChecker(response)

def krdictFetchChecker(response):
    try:
        response = response.data
        if response.total_results > 0:
            return response
        return False
    except:
        return None

async def krdictFetchScraper(text: str):
    response = krdict.scraper.search(query=text, translation_language="english")
    return krdictFetchChecker(response)
