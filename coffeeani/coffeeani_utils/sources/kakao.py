import aiohttp
try:
    from korean_romanizer.romanizer import Romanizer
except ImportError:
    Romanizer = None

import asyncio
import base64
import io
import json
import urllib.parse

from ..models import SearchResult
from ..utils import *

import logging
logger = logging.getLogger(__name__)

try:
    from PIL import Image
    DEP_PIL = True
except:
    DEP_PIL = False

NAME_KAKAO_WEBTOON = "Kakao Webtoon (카카오웹툰)"

COLOR_KAKAO = "#121212"

URL_KAKAO_WEBTOON_SEARCH = "https://gateway-kw.kakao.com/search/v2/content?limit=6&offset=0&word=###KAKAO_VAR###"
URL_KAKAO_WEBTOON_ID = "https://gateway-kw.kakao.com/decorator/v2/decorator/contents/###KAKAO_VAR###"

async def kakao_request(base_url, query=""):
    url = str(base_url).replace("###KAKAO_VAR###", str(query))
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

async def kakao_search_manga(query):
    try:
        raw_data = await kakao_request(URL_KAKAO_WEBTOON_SEARCH, query)
        if not raw_data:
            return None
        if raw_data["meta"]["pagination"]["totalCount"] <= 0:
            return None
    except Exception as err:
        logger.error(err, exc_info=True)
        return None

    embeds = []
    j_data = raw_data.get("data", {})
    j_content = j_data.get("content", [])
    if len(j_content) <= 0:
        logger.debug("No results")
        return None

    for idx, anime_manga in enumerate(j_content):
        payload = SearchResult()
        payload.series_id = anime_manga.get("id", None)
        payload.link = "https://webtoon.kakao.com/content/"+urllib.parse.quote(anime_manga.get("seoId", ""), safe="")+"/"+str(payload.series_id)
        payload.title = anime_manga.get("title", "None")
        payload.description = anime_manga.get("catchphraseThreeLines", None) or anime_manga.get("catchphraseTwoLines", None) or None
        payload.embed_description = kakao_get_description(payload.description)
        payload.image = None
        payload.image_thumbnail = kakao_get_image(anime_manga.get("backgroundImage"))
        payload.info_format = "MANHWA"
        payload.authors = kakao_get_authors(anime_manga)
        payload.country_of_origin = "ko"
        payload.country_of_origin_flag_str = ":flag_kr: "
        payload.names = [anime_manga.get("title", None)]
        payload.tags = kakao_get_tags(anime_manga)
        payload.background_color = anime_manga.get("backgroundColor", None)
        if Romanizer:
            payload.romanized_title = Romanizer(str(payload.title)).romanize().title()
        else:
            payload.romanized_title = None

        manhwa = await kakao_request_manhwa(payload.series_id)
        if manhwa:
            new_description = manhwa.get("synopsis", None)
            payload.description = new_description
            payload.embed_description = kakao_get_description(new_description)
            payload.image = kakao_get_image(manhwa.get("thumbnailImage"))
            payload.image_thumbnail = None
            payload.info_status = "Status: " + str(manhwa.get("status", None)).lower().replace("_", " ").capitalize()
            payload.info_statistics = kakao_get_statistics(manhwa.get("statistics"))
            payload.info_links = f"[Kakao Webtoon]({payload.link})"
            payload.info = "\n".join(filter(None, [payload.info_statistics, payload.info_links]))

        embeds.append(payload.__dict__)
    return (embeds, j_content)

async def kakao_request_manhwa(id):
    j_profile = await kakao_request(URL_KAKAO_WEBTOON_ID, str(id))
    if j_profile.get("data", None):
        return j_profile.get("data", None)
    return None

async def kakao_request_image(image_url):
    if not image_url:
        return None
    url = str(image_url) + ".webp"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.read()
            return io.BytesIO(data)

def kakao_get_description(text):
    condensed_text = description_parser(text, limit_lines=False, limit_char=155, flatten_lines=True)
    translate_link = format_translate(text, "ko", "en")
    if len(translate_link) > 1800:
        translate_link = format_translate(description_parser(text, limit_lines=False, limit_char=1000, flatten_lines=True), "ko", "en")
    if len(translate_link) > 1800:
        translate_link = "https://deepl.com/translator"
    return condensed_text + f"\n[See Translation >]({translate_link})"

def kakao_get_image(image_url):
    if image_url:
        return str(image_url)+".webp"
    return None

def kakao_get_authors(result):
    authors = result.get("authors", [])
    msg = []
    for au in authors:
        name = au.get('name')
        if Romanizer and name and not name.isascii():
            name = name + f' *({Romanizer(str(name)).romanize().title()})*'
        msg.append(f"{str(au.get('type')).lower().replace('_', ' ').capitalize()}: {str(name)}")
    return "\n".join(msg)

def kakao_get_statistics(statistics):
    msg = []
    view_count = statistics.get("viewCount")
    if view_count:
        msg.append(f"👀 {view_count:,}")
    like_count = statistics.get("likeCount")
    if like_count:
        msg.append(f"👍 {like_count:,}")
    return "\n".join(msg)

def kakao_get_tags(manhwa):
    tag = manhwa.get("genre")
    if GENRES_MAP.get(tag):
        return [GENRES_MAP.get(tag)]
    elif tag:
        return [tag]
    return None

async def kakao_build_image_banner(bg_img_url, char_img_url):
    if not bg_img_url and not char_img_url:
        return None
    if not bg_img_url:
        return char_img_url
    if not char_img_url:
        return bg_img_url
    bg_img_raw = await kakao_request_image(bg_img_url)
    bg_img = Image.open(bg_img_raw)
    char_img_raw = await kakao_request_image(char_img_url)
    char_img = Image.open(char_img_raw)
    # Build base image
    left, upper, right, lower = 0, 50, bg_img.width, 350
    final_img = bg_img.crop((left, upper, right, lower))
    # Build opacity overlay
    overlay = Image.new('RGBA', final_img.size, (0,0,0,128)) # 128/255 -> 0.5 opacity
    final_img = Image.alpha_composite(final_img.convert('RGBA'), overlay)
    # Build char_img
    char_img_width = int((280 / char_img.height) * char_img.width)
    char_img_resized = char_img.resize((char_img_width, 280))
    final_img.paste(char_img_resized, (final_img.width - char_img_resized.width - 20, 20), char_img_resized)
    # Save to image
    output = io.BytesIO()
    final_img.save(output, format="WEBP")
    output.seek(0)
    # data_uri = base64.b64encode(output.getvalue()).decode("utf-8")
    # return "data:image/webp;base64," + str(data_uri)
    return output
