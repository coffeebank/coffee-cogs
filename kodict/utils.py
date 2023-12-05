import discord
import urllib.parse

import aiohttp
import asyncio
import kodict_core
from korean_romanizer.romanizer import Romanizer

from .coffee_redbot.core.utils.view import SimpleMenu


## Utility Commands

def truncate(text: str, max: int, extension: str="…"):
    if len(text) > max:
        return text[:max-1]+extension
    else: return text

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
        description=kodict_core.services.krdict.krdict_results_body(krdict_result),
        colour=embed_colour
    )
    for idx, kr_def in enumerate(krdict_result.definitions):
        krdict_definition = kodict_core.services.krdict.krdict_results_definition(kr_def, idx)
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
    if len(" ・ ".join(alt_links)) > 1013:
        alt_links = [
            "Wiktionary: [EN](https://en.wiktionary.org), [KO](https://ko.wiktionary.org)",
            "Google Translate: [EN](https://translate.google.com)"
        ]
    if Romanizer(str(text)).romanize() != text:
        text_romanization = str(Romanizer(str(text)).romanize())
    else:
        text_romanization = None
    if Romanizer(str(deepl_results)).romanize() != deepl_results:
        deepl_results = "\n".join([deepl_results, truncate(str(Romanizer(str(deepl_results)).romanize()), 250)])
    desc = "\n".join(filter(None, [text_romanization, description]))
    e = discord.Embed(title=truncate(str(text), 100), description=desc, colour=embed_colour)
    e.add_field(name="Translation", value=">>> "+truncate(str(deepl_results), 1019), inline=False)
    e.add_field(name="More Links", value=" ・ ".join(alt_links), inline=False)
    e.set_footer(text="Results from DeepL. No Krdict search results found.")
    return e

async def embed_fallback(text, description=None, footer=None, embed_colour: discord.Colour=None):
    safe_text = urllib.parse.quote(text, safe='')
    e = discord.Embed(title=truncate(str(text), 100), description=description, colour=embed_colour)
    e.add_field(name="Krdict (한국어기초사전)", value=f"https://krdict.korean.go.kr/eng/dicMarinerSearch/search?mainSearchWord={safe_text}")
    e.add_field(name="Wiktionary", value=f"https://en.wiktionary.org/w/index.php?fulltext=0&search={safe_text}")
    e.add_field(name="DeepL Translate", value=f"https://deepl.com/translator#ko/en/{safe_text}")
    e.add_field(name="Google Translate", value=f"https://translate.google.com/?text={safe_text}")
    if footer:
        e.set_footer(text=footer)
    return e


## Bot Commands

async def command_kodict(ctx, text: str, krdict_key=None, deepl_key=None, embed_colour=None):
    # Respond early to prevent slash interaction from expiring
    response = await SimpleMenu(pages=[{'content': 'Searching...'}], timeout=90).start(ctx)
    results = await kodict_core.fetch_all(text, krdict_key, deepl_key)
    try:
        if results.get("krdict", None):
            attribution = ["Krdict (한국어기초사전)"]
            if results.get("deepl", None):
                attribution.append("DeepL")
            send_embeds = await embed_krdict(results.get("krdict"), attribution, embed_colour)
            await SimpleMenu(pages=send_embeds, timeout=90).replace(ctx, response)
        elif results.get("deepl", None):
            deepl_embed = await embed_deepl(text, results.get("deepl"), None, embed_colour)
            await response.edit(content="", embed=deepl_embed)
        else:
            fallback_embed = await embed_fallback(text, None, "No results from Krdict API.", embed_colour)
            await response.edit(content="", embed=fallback_embed)
    except Exception as err:
        # User cancelled operation, ctx will return NotFound
        await response.edit(content="Error: Please try again. Possible issues include: cancelled command, network errors, or text is too long.")
        pass
