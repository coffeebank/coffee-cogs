import aiohttp
import asyncio

from kodict.utils_deepl import *
from kodict.utils_krdict import *

async def fetch_all(text, krdict_key=None, deepl_key=None):
    # Try Krdict API and Parser first
    results = await fetch_krdict(text, krdict_key)
    if results:
        return {"krdict": results}
    # Try DeepL
    deepl_text = await fetch_deepl(text, deepl_key)
    if deepl_text:
        results = await fetch_krdict(deepl_text, krdict_key)
    if results:
        return {"krdict": results, "deepl": deepl_text}
    else:
        return {"deepl": deepl_text}
