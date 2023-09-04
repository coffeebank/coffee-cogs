import asyncio
import aiohttp
import json

from .utils import *

URL_MANGADEX = "https://api.mangadex.org"

async def mangadex_request(branch, params):
    url = URL_MANGADEX+"/"+branch
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            return await response.json()

async def mangadex_search_manga(query):
    try:
        raw_data = await mangadex_request("manga", params=[("title", str(query))])
        if raw_data.get("total", 0) <= 0:
            return None
    except Exception as err:
        print("[coffeeani]", "[utils_mangadex]", err)
        return None

    embeds = []
    
    for idx, anime_manga in enumerate(raw_data.get("data", [])):
        attributes = anime_manga.get("attributes", {})

        series_id = anime_manga.get("id", 0)
        link = mangadex_get_link(series_id)
        title = mangadex_get_title(anime_manga) or "No Title"
        description = mangadex_get_description(anime_manga)
        time_left = None
        image = mangadex_get_image_banner(series_id)
        embed_description = description_parser(description)
        studios = None
        external_links = mangadex_get_external_links(anime_manga)
        info_format = format_manga_type("MANGA", attributes.get("originalLanguage", None))
        info_status = "Status: "+str(attributes.get("status", None)).lower().replace("_", " ").capitalize()
        info_epschaps = None
        info_start_end = None
        info_start_year = format_string(attributes.get("year", None))
        info_links = f"[MangaDex]({link})"
        info = "\n".join(filter(None, [info_epschaps, info_links]))
        country_of_origin = attributes.get("originalLanguage", None)
        country_of_origin_flag_str = None
        relations = None
        names = None
        tags = None

        payload = {
          'series_id': series_id,
          'link': link,
          'title': title,
          'description': description, 
          'time_left': time_left,
          'image': image,
          'embed_description': embed_description,
          'studios': studios,
          'external_links': external_links,
          'info_format': info_format,
          'info_status': info_status,
          'info_epschaps': info_epschaps,
          'info_start_end': info_start_end,
          'info_start_year': info_start_year,
          'info_links': info_links,
          'info': info,
          'country_of_origin': country_of_origin,
          'country_of_origin_flag_str': country_of_origin_flag_str,
          'relations': relations,
          'names': names,
          'tags': tags,
        }
        embeds.append(payload)
    return embeds, raw_data

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
    description = attributes.get("description", None)
    if not description:
        return None
    first_key = get_array_first_key(attributes.get("description", None))
    if not first_key:
        return None
    return description.get(first_key, None)

def mangadex_get_image_banner(id: str):
    return "https://og.mangadex.org/og-image/manga/"+id

def mangadex_get_external_links(anime_manga):
    attributes = anime_manga.get("attributes", {})
    links = attributes.get("links", None)
    if not links:
        return None
    external_links = []
    for k, v in links.items():
        if "http" in v:
            external_links.append(f"[{str(k).capitalize()}]({str(v)})")
    if len(external_links) > 0:
        return ", ".join(external_links)
    return None

def get_array_first_key(arr):
    if arr:
        return next(iter(arr))
    return None
