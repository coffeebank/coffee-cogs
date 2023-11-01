import asyncio
import aiohttp
import json
import urllib.parse

from ..models import SearchResult
from ..utils import *

import logging
logger = logging.getLogger(__name__)

NAME_BATOTO = "Batoto"

COLOR_BATOTO = "#13667A"

URL_BATOTO = "https://bato.to/apo/"

SEARCH_BATOTO_QUERY = """
query get_content_searchComic($select: SearchComic_Select) {
  get_content_searchComic(
    select: $select
  ) {
    reqPage reqSize reqSort reqWord newPage
    paging { 
      total pages page init size skip limit
    }
    items {
      id
      data {
        id
        dbStatus
        isNormal isHidden isDeleted
        dateCreate datePublic dateModify dateUpload dateUpdate
        slug urlPath
        name altNames
        authors artists
        genres
        origLang tranLang
        uploadStatus
        originalStatus originalPubFrom originalPubTill
        urlCover600 urlCover300 urlCoverOri
        stat_is_hot stat_is_new
        stat_count_emotions {
          field count
        }
        stat_count_statuss {
          field count
        }
        stat_score_avg stat_score_bay
        stat_count_chapters_normal
        stat_count_chapters_others
      }
    }
  }
}
"""

async def batoto_request(query, variables=None):
    if variables is None:
        variables = {}
    request_json = {"query": query, "variables": variables}
    headers = {"content-type": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.post(URL_BATOTO, data=json.dumps(request_json), headers=headers) as response:
            return await response.json()

async def batoto_search_manga(query: str):
    try:
        variables = {"select": { "page": 1, "size": 10, "where": "browse", "word": query }}
        raw_data = await batoto_request(SEARCH_BATOTO_QUERY, variables)
        data = raw_data["data"]["get_content_searchComic"]["items"]
    except Exception as err:
        logger.error(err, exc_info=True)
        return None

    if len(data) <= 0:
        logger.debug("No results")
        return None

    embeds = []
    embeds_non_en = []
    embeds_adult = []

    for idx, anime_manga_obj in enumerate(data):
        anime_manga = anime_manga_obj.get("data", {})
        payload = SearchResult()
        payload.series_id = anime_manga.get("id", 0)
        payload.link = "https://bato.to"+anime_manga.get("urlPath", "/search?word="+urllib.parse.quote(query, safe=""))
        payload.title = anime_manga.get("name", None) or anime_manga.get("slug", "").replace("-", "") or "No Title"
        payload.description = batoto_get_description(anime_manga)
        payload.image = None
        payload.image_thumbnail = anime_manga.get("urlCover600", None) or anime_manga.get("urlCover300", None) or anime_manga.get("urlCoverOri", None)
        payload.embed_description = description_parser(payload.description)
        payload.studios = None
        payload.external_links = None
        payload.info_format = format_manga_type("MANGA", anime_manga.get("origLang", None))
        payload.info_status = "Status: "+str(anime_manga.get("originalStatus", anime_manga.get("uploadStatus", None))).lower().replace("_", " ").capitalize()
        payload.info_epschaps = batoto_get_epschaps(anime_manga)
        payload.info_start_end = None
        payload.info_start_year = format_string(anime_manga.get("originalPubFrom", None))
        payload.info_links = f"[Batoto]({payload.link})"
        payload.info = "\n".join(filter(None, [payload.info_epschaps, payload.info_links]))
        payload.country_of_origin = anime_manga.get("origLang", None)
        payload.country_of_origin_flag_str = get_country_of_origin_flag_str(payload.country_of_origin)
        payload.relations = None
        payload.names = anime_manga.get("altNames", None)
        payload.tags = batoto_get_tags(anime_manga)

        genres = anime_manga.get("genres", None)
        tran_lang = anime_manga.get("tranLang", None)
        if genres and any([x in set(genres) for x in ["adult", "hentai", "mature"]]):
            embeds_adult.append(payload.__dict__)
        elif tran_lang and tran_lang.lower().split("-")[0] not in ["en"]:
            embeds_non_en.append(payload.__dict__)
        else:
            embeds.append(payload.__dict__)
    return (embeds+embeds_non_en+embeds_adult, data)

def batoto_get_description(anime_manga):
    emotions_map = {
        "upvote": "👍",
        "funny": "😝",
        "love": "💖",
        "surprised": "😯",
        "scared": "😯",
        "angry": "😡",
        "sad": "😢",
    }
    field_emotions = None
    emotions = []
    stat_count_emotions = anime_manga.get("stat_count_emotions", None)
    if stat_count_emotions:
        for sce in stat_count_emotions:
            field_emoji = emotions_map.get(sce.get("field", "none"), sce.get("field", None))
            if not field_emoji:
                continue
            emotions.append(f"{field_emoji} {str(sce.get('count', 0))}")
    if emotions:
        field_emotions = " ・ ".join(emotions)

    field_badges = None
    badges = []
    genres = anime_manga.get("genres", None)
    tran_lang = anime_manga.get("tranLang", None)
    if genres and any([x in set(genres) for x in ["adult", "hentai", "mature"]]):
        badges.append("🔞")
    if tran_lang and tran_lang != "en":
        flag = get_country_of_origin_flag_str(str(tran_lang))
        badges.append(flag)
    if anime_manga.get("stat_is_hot", None):
        badges.append("🔥")
    if anime_manga.get("stat_is_new", None):
        badges.append("🆕")
    if badges:
        field_badges = " ".join(badges)
    
    return "\n\n".join(filter(None, [field_emotions, field_badges]))

def batoto_get_epschaps(anime_manga):
    chapter_count = anime_manga.get("stat_count_chapters_normal", None)
    if chapter_count:
        return f"Chapters: {str(chapter_count)}"
    return None

def batoto_get_tags(anime_manga):
    tags = []
    genres = anime_manga.get("genres", [])
    for tag_genres in genres:
        tags.append(str(tag_genres).replace("_", " ").capitalize())
    if tags:
        return tags
    return None
