import urllib.parse

import aiohttp
import asyncio
from korean_romanizer.romanizer import Romanizer
import lxml

import kodict.krdict as krdict

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

async def fetch_krdict(text, krdict_key=None):
    krResults = None
    # Fetch using Krdict API
    # Very rudimentary check to pass English onto Krdict Scraper (not supported by API)
    if krdict_key is not None and text.isascii() is False:
        krResults = await krdict_fetch_api(krdict_key, text)
    if krResults:
        return krResults
    # Fetch using Krdict Scraper
    return await krdict_fetch_scraper(text)

async def krdict_fetch_api(api_key: str, text: str):
    krdict.set_key(api_key)
    try:
        response = await krdict.search(query=text, translation_language="english", raise_api_errors=True)
        return krdict_fetch_checker(response)
    except Exception:
        return None

async def krdict_fetch_scraper(text: str):
    try:
        response = await krdict.scraper.search(query=text, translation_language="english")
        return krdict_fetch_checker(response)
    except Exception:
        return None

def krdict_fetch_checker(response):
    try:
        response = response.data
        if response.total_results > 0:
            return response
        return False
    except Exception:
        return None

def krdict_results_body(krdict_result):
    return " ・ ".join(filter(None, [
        krdict_results_pronunciation(krdict_result),
        krdict_results_origin(krdict_result),
        krdict_results_parts_of_speech(krdict_result),
        krdict_results_word_grade(krdict_result)
    ]))

def krdict_results_pronunciation(krdict_result):
    try:
        pronunciation_kr = str(krdict_result.pronunciation)
    except (AttributeError, Exception):
        pronunciation_kr = None
    try:
        romanization = str(Romanizer(str(krdict_result.word)).romanize())
    except (AttributeError, Exception):
        romanization = None
    pronunciation = " ".join(filter(None, [pronunciation_kr, romanization]))
    return pronunciation

def krdict_results_origin(krdict_result):
    try:
        return str(krdict_result.origin)
    except (AttributeError, Exception):
        return None

def krdict_results_parts_of_speech(krdict_result):
    try:
        if krdict_result.part_of_speech and (krdict_result.part_of_speech not in ["품사 없음", "None", None]):
            parts_of_speech_raw = str(krdict_result.part_of_speech)
            eng_pos = str(parts_of_speech_blocks.get(parts_of_speech_raw, None))
            return "` "+" ".join(filter(None, [parts_of_speech_raw, eng_pos]))+" `"
    except (AttributeError, Exception):
        return None

def krdict_results_word_grade(krdict_result):
    try:
        if krdict_result.vocabulary_level and (krdict_result.vocabulary_level not in ["None", None]):
            word_grade_raw = str(krdict_result.vocabulary_level)
            level_gauge = str(word_grade_blocks.get(word_grade_raw, None))
            return "` "+" ".join(filter(None, [word_grade_raw, level_gauge]))+" `"
    except (AttributeError, Exception):
        return None

def krdict_results_definition(krdict_definition, idx: int=None):
    # Only `if idx` will return False when idx == 0
    if idx is not None:
        try:
            idx = int(krdict_definition.order)
        except AttributeError:
            idx = int(idx)+1
        idx_str = str(idx)+"."
    else:
        idx_str = "-"
    try:
        ko_def = str(krdict_definition.definition)
    except AttributeError:
        ko_def = None
    try:
        en_trans = krdict_definition.translations[0]
        en_word = str(en_trans.word)
        en_def = str(en_trans.definition)
    except (AttributeError, IndexError) as err:
        en_trans = None
        en_word = None
        en_def = f"[See translation on DeepL](https://www.deepl.com/translator#ko/en/{urllib.parse.quote(str(ko_def), safe='')})"
    return {
      "name": " ".join(filter(None, [idx_str, en_word])),
      "value": "\n".join(filter(None, [en_def, ko_def]))
    }
