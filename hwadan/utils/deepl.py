import urllib.parse

import aiohttp
import asyncio

async def fetch_deepl(text: str, deepl_key=None):
    if deepl_key is not None:
        # EN -> KO
        if str(text).isascii():
            deepl_results = deepl_fetch_checker(text, await deepl_fetch_api(text, deepl_key, "EN", "KO"))
            if deepl_results not in [None, False]:
                return deepl_results
        # KO -> EN
        return deepl_fetch_checker(text, await deepl_fetch_api(text, deepl_key, "KO", "EN"))
    else:
        return None

async def deepl_fetch_api(text: str, api_key: str, source_lang: str="EN", target_lang: str="KO"):
    deeplUrl = "https://api-free.deepl.com/v2/translate"
    payload = f"text={urllib.parse.quote(text, safe='')}&source_lang={source_lang}&target_lang={target_lang}"
    headers = {
        "Authorization": "DeepL-Auth-Key "+str(api_key),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(deeplUrl, headers=headers, data=payload) as resp:
                deeplJson = await resp.json()
                return deeplJson
    except Exception:
        return None

def deepl_fetch_checker(text: str, deeplJson):
    try:
        deepl_translated_text = deeplJson["translations"][0].get("text")
        if text == deepl_translated_text:
            # Deepl failed to translate properly
            return False
        return str(deepl_translated_text)
    except Exception:
        return False
