import asyncio
import aiohttp
import json

from ..models import SearchResult
from ..utils import *

import logging
logger = logging.getLogger(__name__)

NAME_BANGUMI = "Bangumi"

COLOR_BANGUMI = "#f09199"

URL_BANGUMI = "https://api.bgm.tv/v0/search/subjects?limit=10"

BANGUMI_TYPE = {
  "anime": 2,
  "manga": 1,
}

SEARCH_BANGUMI_QUERY = {
  "keyword": "",
  "sort": "rank",
  "filter": {
    "type": [],
  }
}

async def bangumi_request(bangumi_type="anime", search="鐵扇公主"):
  request_json = SEARCH_BANGUMI_QUERY
  request_json["keyword"] = search
  request_json["filter"]["type"] = [BANGUMI_TYPE[bangumi_type]]
  headers = {"Content-Type": "application/json", "User-Agent": "czy0729/Bangumi/6.4.0 (Android) (http://github.com/czy0729/Bangumi)"}
  async with aiohttp.ClientSession() as session:
    async with session.post(URL_BANGUMI, json=request_json, headers=headers) as response:
      if response.status != 200:
        logger.error(f"Failed to fetch {URL_BANGUMI}. Status code: {response.status}")
        return None
      return await response.json()

async def bangumi_search_anime_manga(bangumi_type, title):
  try:
    raw_data = await bangumi_request(bangumi_type, title)
    data = raw_data["data"]
  except Exception as err:
    logger.error(err, exc_info=True)
    return None
  
  if not data:
    logger.debug("No results")
    return None
  if len(data) <= 0:
    logger.debug("No results")
    return None

  embeds = []
  embeds_adult = []
  idx_total = len(data)

  for idx, anime_manga in enumerate(data):
    payload = SearchResult()
    payload.series_id = anime_manga.get("id", 0)
    payload.link = f"https://bgm.tv/subject/{payload.series_id}"
    payload.title = anime_manga["name"] or anime_manga["name_cn"] or "No Title"
    payload.description = anime_manga.get("summary", None)
    payload.image_thumbnail = anime_manga.get("image", None)
    payload.external_links = bangumi_get_external_links(anime_manga, payload.link)
    payload.info_format = bangumi_get_info_format(anime_manga)
    payload.info_status = "More Info"
    payload.info_epschaps = bangumi_get_info_epschaps(anime_manga, bangumi_type)
    payload.info_links = bangumi_get_info_links(anime_manga, payload.link)
    payload.info = "\n".join(filter(None, [payload.info_epschaps, payload.info_links]))
    payload.country_of_origin_flag_str = ""
    payload.names = bangumi_get_names(anime_manga)
    payload.embed_description = payload.description[:4000]
    payload.tags = bangumi_get_tags(anime_manga)

    if anime_manga.get("nsfw", None) == True:
      embeds_adult.append(payload.__dict__)
    else:
      embeds.append(payload.__dict__)
  return (embeds+embeds_adult, data)

def bangumi_get_info_epschaps(anime_manga, bangumi_type):
  epschaps = ""
  if bangumi_type == "manga":
    epschaps += "Chapters: "
  else:
    epschaps += "Episodes: "
  if anime_manga.get("eps"):
    epschaps += str(anime_manga.get("eps"))
    return epschaps
  return None

def bangumi_get_info_links(anime_manga, link):
  bangumi_str = ""
  if anime_manga.get("nsfw", None) == True:
    bangumi_str += "🔞 "
  bangumi_str += f"[Bangumi]({link})"
  return bangumi_str

def bangumi_get_external_links(anime_manga, link):
  urls_official = []
  url_official = next((item for item in anime_manga.get("infobox", []) if item["key"] == "官方网站"), {})
  if url_official.get("value"):
    urls_official = [f'[官方网站 (Official)]({url_official.get("value")})']

  urls_infobox = []
  urls = next((item for item in anime_manga.get("infobox", []) if item["key"] == "链接"), None)
  if urls:
    urls_infobox = [f'[{v["k"]}]({v["v"]})' for v in urls["value"]]

  if urls_official or urls_infobox:
    return ", ".join(filter(None, urls_official + urls_infobox))
  else:
    return None

def bangumi_get_info_format(anime_manga):
  info_format = ""
  if anime_manga.get("platform"):
    info_format += anime_manga.get("platform") + " "
  if anime_manga.get("date"):
    info_format += anime_manga.get("date")

  if info_format:
    return info_format
  else:
    return None

def bangumi_get_names(anime_manga):
  names_infobox = []
  names = next((item for item in anime_manga.get("infobox", []) if item["key"] == "别名"), None)
  if names:
    names_infobox = [v["v"] for v in names["value"]]

  names_full = [anime_manga.get("name_cn", None)] + names_infobox
  names_send = filter(None, names_full)
  if anime_manga.get("name_cn", None) or names_infobox:
    return names_send
  else:
    return None

def bangumi_get_tags(anime_manga):
  tags_raw = anime_manga.get("tags", [])
  tags = [t["name"] for t in tags_raw]
  if len(tags) > 0:
    return tags[:19]
  else:
    return None
