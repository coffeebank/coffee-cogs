import asyncio
import aiohttp
import json

from ..models import SearchResult
from ..utils import *

import logging
logger = logging.getLogger(__name__)

NAME_MANGADEX = "MangaDex"

COLOR_MANGADEX = "#FF6740"

URL_MANGADEX = "https://api.mangadex.org"

EXTERNAL_LINKS_MAP = {
  "al": "Anilist",
  "ap": "Anime-Planet",
  "amz": "Amazon",
  "bw": "bookwalker.jp",
  "cdj": "CDJapan",
  "ebj": "ebookjapan",
  "engtl": "English Translation",
  "kt": "Kitsu",
  "mal": "MAL",
  "mu": "MangaUpdates",
  "nu": "NovelUpdates",
}

EXTERNAL_LINKS_REPLACE_MAP = {
  "al": "https://anilist.co/manga/@@@@@",
  "ap": "https://www.anime-planet.com/manga/@@@@@",
  "kt": "https://kitsu.io/manga/@@@@@",
  "mal": "https://myanimelist.net/manga/@@@@@",
  "mu": "https://www.mangaupdates.com/series/@@@@@",
  "nu": "https://www.novelupdates.com/series/@@@@@",
}

async def mangadex_request(branch, params):
    url = URL_MANGADEX+"/"+branch
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            return await response.json()

async def mangadex_search_manga(query):
    try:
        raw_data = await mangadex_request("manga", params=[("title", str(query))])
        if not raw_data:
            return None
        if raw_data.get("total", 0) <= 0:
            return None
    except Exception as err:
        logger.error(err, exc_info=True)
        return None

    data = raw_data.get("data", [])
    if len(data) <= 0:
        logger.debug("No results")
        return None

    embeds = []
    embeds_adult = []
    
    for idx, anime_manga in enumerate(data):
        attributes = anime_manga.get("attributes", {})
        payload = SearchResult()
        payload.series_id = anime_manga.get("id", 0)
        payload.link = mangadex_get_link(payload.series_id)
        payload.title = mangadex_get_title(anime_manga) or "No Title"
        payload.description = mangadex_get_description(anime_manga)
        payload.image = mangadex_get_image_banner(payload.series_id)
        payload.embed_description = mangadex_get_description_embed(payload.description)
        payload.external_links = mangadex_get_external_links(anime_manga)
        payload.info_format = format_manga_type("MANGA", attributes.get("originalLanguage", None))
        payload.info_status = "Status: "+str(attributes.get("status", None)).lower().replace("_", " ").capitalize()
        payload.info_epschaps = mangadex_get_info_epschaps(anime_manga)
        payload.info_start_year = format_string(attributes.get("year", None))
        payload.info_links = mangadex_get_info_links(anime_manga, payload.link)
        payload.info = "\n".join(filter(None, [payload.info_epschaps, payload.info_links]))
        payload.country_of_origin = attributes.get("originalLanguage", None)
        payload.country_of_origin_flag_str = get_country_of_origin_flag_str(payload.country_of_origin)
        payload.names = mangadex_get_names(anime_manga)
        payload.tags = mangadex_get_tags(anime_manga)

        content_rating = attributes.get("contentRating", None)
        if content_rating and content_rating not in ["safe", "suggestive"]:
            embeds_adult.append(payload.__dict__)
        else:
            embeds.append(payload.__dict__)
    return (embeds+embeds_adult, raw_data)

def mangadex_get_link(id: str):
    return "https://mangadex.org/title/"+id

def mangadex_get_title(anime_manga):
    attributes = anime_manga.get("attributes", None)
    if not attributes:
        return None
    title = attributes.get("title", None)
    if title:
        return title.get(next(iter(title)), None)
    alt_titles = attributes.get("altTitles", None)
    if alt_titles:
        return alt_titles.get(next(iter(alt_titles)), None)
    return None

def mangadex_get_description(anime_manga):
    attributes = anime_manga.get("attributes", {})
    description = attributes.get("description")
    if not description:
        return None
    # First, we check for [en] description
    if description.get("en"):
        return description.get("en")
    # Then, if there isn't, we fall back to [originalLanguage] + translate link
    original_language = attributes.get("originalLanguage")
    description_original_language = description.get(str(original_language))
    if original_language and description_original_language:
        description_original_language_short = description_parser(description_original_language, limit_lines=False, limit_char=155, flatten_lines=True)
        description_original_language_medium = description_parser(description_original_language, limit_lines=False, limit_char=600, flatten_lines=True)
        return f"{description_original_language_short}\n[See translation >]({format_translate(description_original_language_medium, original_language, 'en')})"
    # Finally, if there isn't, we use the first key and add the language in front
    first_key_language = get_array_first_key(description)
    description_first_key = description.get(first_key_language, None)
    if first_key_language and description_first_key:
        description_first_key_short = description_parser(description_first_key, limit_lines=False, limit_char=155, flatten_lines=True)
        description_first_key_medium = description_parser(description_first_key, limit_lines=False, limit_char=600, flatten_lines=True)
        # Translate might not support the language, so we use 'auto'
        return f"**🔤 {str(first_key_language)} :** \n{description_first_key_short}\n[See translation >]({format_translate(description_first_key_medium, 'a', 'en')})"
    return None

def mangadex_get_description_embed(description):
    if description is None:
        return None
    if "See translation" in description:
        return description
    return description_parser(description)

def mangadex_get_image_banner(id: str):
    return "https://og.mangadex.org/og-image/manga/"+id

def mangadex_get_external_links(anime_manga):
    attributes = anime_manga.get("attributes", {})
    links = attributes.get("links", None)
    if not links:
        return None
    external_links = []
    for k, v in links.items():
        k_lengthen = EXTERNAL_LINKS_MAP.get(str(k).lower(), str(k).lower().capitalize())
        if "http" in v:
            external_links.append(f"[{str(k_lengthen)}]({str(v)})")
    if len(external_links) > 0:
        return ", ".join(external_links)
    return None

def mangadex_get_info_epschaps(anime_manga):
    attributes = anime_manga.get("attributes", {})
    # TODO: Volumes
    # volumes = attributes.get("lastVolume", None)
    chapters = attributes.get("lastChapter", None)
    if chapters:
        return f"Chapters: {str(chapters)}"
    return None

def mangadex_get_info_links(anime_manga, link=None):
    final_links = []
    attributes = anime_manga.get("attributes", {})
    if not link:
        link = mangadex_get_link(attributes.get("id", None))
    content_rating = attributes.get("contentRating", None)
    if content_rating and content_rating not in ["safe", "suggestive"]:
        final_links.append(f"🔞 [MangaDex]({link})")
    else:
        final_links.append(f"[MangaDex]({link})")
    links = attributes.get("links", None)
    if links:
        for k, v in links.items():
            if EXTERNAL_LINKS_REPLACE_MAP.get(str(k), None):
                k_lengthen = EXTERNAL_LINKS_MAP.get(str(k), str(k).lower().capitalize())
                url_template = EXTERNAL_LINKS_REPLACE_MAP.get(str(k), None)
                url = url_template.replace("@@@@@", str(v))
                final_links.append(f"[{k_lengthen}]({url})")
    return ", ".join(final_links)

def mangadex_get_names(anime_manga):
    names = []
    attributes = anime_manga.get("attributes", {})
    original_language = attributes.get("originalLanguage", None)
    original_language_romanized = None
    if original_language:
        original_language_romanized = str(original_language).split("-")[0]+"-ro"
    title = attributes.get("title", None)
    if title.get(original_language, None):
        names.append(title.get(original_language, None))
    if original_language_romanized and title.get(original_language_romanized, None):
        names.append(title.get(original_language_romanized, None))
    alt_titles_arr = attributes.get("altTitles", None)
    for alt_titles in alt_titles_arr:
        if alt_titles.get(original_language, None):
            names.append(alt_titles.get(original_language, None))
        if original_language_romanized and alt_titles.get(original_language_romanized, None):
            names.append(alt_titles.get(original_language_romanized, None))
    return names

def mangadex_get_tags(anime_manga):
    tags = []
    tags_other = []
    attributes = anime_manga.get("attributes", {})
    tags_arr = attributes.get("tags")
    for tag_dict in tags_arr:
        attr = tag_dict.get("attributes", {})
        attr_group = attr.get("group", None)
        attr_name = attr.get("name", {})
        attr_name_en = attr_name.get("en", None)
        if attr_group == "genre" and attr_name_en:
            tags.append(attr_name_en)
        elif attr_name_en:
            tags_other.append(attr_name_en)
    return tags+tags_other
