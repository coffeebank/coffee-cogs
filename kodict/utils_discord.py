import discord
import urllib.parse

import aiohttp
import asyncio
from korean_romanizer.romanizer import Romanizer

from kodict.utils_deepl import *
from kodict.utils_krdict import *
import kodict.krdict as krdict

async def embed_krdict(krdict_results, attribution: list[str]=["Krdict (한국어기초사전)"], embed_color: discord.Colour=None):
    sendEmbeds = []
    attribution = "Results from "+", ".join(attribution)
    try:
        total = str(min(int(krdict_results.total_results), 10))
    except:
        total = "..."
    for result_idx, krdict_result in enumerate(krdict_results.results):
        e = await embed_krdict_result(krdict_result, result_idx, str(total), attribution, embed_color)
        sendEmbeds.append({"content": "", "embed": e})
    return sendEmbeds

async def embed_krdict_result(krdict_result, result_idx: int, total: str, attribution: str, embed_colour: discord.Colour=None):
    e = discord.Embed(
        title=str(krdict_result.word),
        url=str(krdict_result.url),
        description=krdict_results_body(krdict_result),
        colour=embed_colour
    )
    for idx, kr_def in enumerate(krdict_result.definitions):
        krdict_definition = krdict_results_definition(kr_def, idx)
        e.add_field(
            name=krdict_definition.get("name"),
            value=krdict_definition.get("value")
        )
    e.set_footer(
        text=" ・ ".join(filter(None, [
            str(attribution),
            str(result_idx+1)+"/"+str(total)
        ])))
    return e

async def embed_deepl(text, deepl_results=None, description=None, embed_colour: discord.Colour=None):
    safe_text = urllib.parse.quote(text, safe='')
    alt_links = [
      f"Wiktionary: [EN](https://en.wiktionary.org/w/index.php?fulltext=0&search={safe_text}), [KO](https://ko.wiktionary.org/w/index.php?fulltext=0&search={safe_text})",
      f"Google Translate: [EN](https://translate.google.com/?text={safe_text})"
    ]
    if Romanizer(str(text)).romanize() != text:
        text_romanization = str(Romanizer(str(text)).romanize())
    else:
        text_romanization = None
    if Romanizer(str(deepl_results)).romanize() != deepl_results:
        deepl_results = "\n".join([deepl_results, str(Romanizer(str(deepl_results)).romanize())])
    desc = "\n".join(filter(None, [text_romanization, description]))
    e = discord.Embed(title=str(text), description=desc, colour=embed_colour)
    e.add_field(name="DeepL Translate", value=str(deepl_results), inline=False)
    e.add_field(name="More Links", value=" ・ ".join(alt_links), inline=False)
    e.set_footer(text="Results from DeepL. No Krdict search results found.")
    return e

async def embed_fallback(text, description=None, footer=None, embed_colour: discord.Colour=None):
    safe_text = urllib.parse.quote(text, safe='')
    e = discord.Embed(title=str(text), description=str(description), colour=embed_colour)
    e.add_field(name="Krdict (한국어기초사전)", value=f"https://krdict.korean.go.kr/eng/dicSearch/search?nation=eng&nationCode=6&mainSearchWord={safe_text}")
    e.add_field(name="Wiktionary", value=f"https://en.wiktionary.org/w/index.php?fulltext=0&search={safe_text}")
    e.add_field(name="DeepL Translate", value=f"https://deepl.com/translator#ko/en/{safe_text}")
    e.add_field(name="Google Translate", value=f"https://translate.google.com/?text={safe_text}")
    if footer:
        e.set_footer(text=footer)
    return e
