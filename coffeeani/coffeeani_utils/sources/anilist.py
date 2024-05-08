# Parts of this file contains code from:
# Jintaku, Wyn: AGPL-3.0 License

import asyncio
import datetime
import json
import re

import aiohttp

from ..models import SearchResult
from ..utils import *

import logging
logger = logging.getLogger(__name__)

NAME_ANILIST = "Anilist"

COLOR_ANILIST = "#3498DB"

URL_ANILIST = "https://graphql.anilist.co"

SEARCH_ANILIST_ANIME_MANGA_QUERY = """
query ($id: Int, $page: Int, $search: String, $type: MediaType) {
  Page (page: $page, perPage: 10) {
    media (id: $id, search: $search, type: $type) {
      id idMal
      description(asHtml: false)
      title {
        english romaji native
      }
      format
      synonyms
      coverImage {
        medium color
      }
      bannerImage
      averageScore meanScore
      status
      source
      startDate {
        year month day
      }
      endDate {
        year month day
      }
      episodes
      chapters volumes
      externalLinks {
        url site
      }
      nextAiringEpisode {
        airingAt timeUntilAiring episode
      }
      countryOfOrigin
      genres
      tags {
        name isMediaSpoiler
      }
      studios {
        edges {
          node {
            name siteUrl
          }
          isMain
        }
      }
      relations {
        nodes {
          id
          title {
            english romaji native userPreferred
          }
          format
          season seasonYear
          countryOfOrigin
        }
      }
      isAdult
    }
  }
}
"""

SEARCH_ANILIST_CHARACTER_QUERY = """
query ($id: Int, $page: Int, $search: String) {
  Page(page: $page, perPage: 10) {
    characters(id: $id, search: $search) {
      id
      description (asHtml: true),
      name {
        first last native
      }
      image {
        large
      }
      media {
        nodes {
          id
          type
          title {
            english romaji native userPreferred
          }
        }
      }
    }
  }
}
"""

SEARCH_ANILIST_USER_QUERY = """
query ($id: Int, $page: Int, $search: String) {
    Page (page: $page, perPage: 10) {
        users (id: $id, search: $search) {
            id
            name
            siteUrl
            avatar {
                    large
            }
            about (asHtml: true),
            stats {
                watchedTime
                chaptersRead
            }
            favourites {
            manga {
              nodes {
                id
                title {
                  romaji
                  english
                  native
                  userPreferred
                }
              }
            }
            characters {
              nodes {
                id
                name {
                  first
                  last
                  native
                }
              }
            }
            anime {
              nodes {
                id
                title {
                  romaji
                  english
                  native
                  userPreferred
                }
              }
            }
            }
        }
    }
}
"""

async def anilist_request(query, variables=None):
    if variables is None:
        variables = {"search": str(query), "page": 1, "type": "ANIME"}
    request_json = {"query": query, "variables": variables}
    headers = {"content-type": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.post(URL_ANILIST, data=json.dumps(request_json), headers=headers) as response:
            return await response.json()

async def anilist_search_anime_manga(cmd, entered_title, isDiscord=False):
    variables = {"search": entered_title, "page": 1, "type": cmd}
    
    try:
        raw_data = await anilist_request(SEARCH_ANILIST_ANIME_MANGA_QUERY, variables)
        data = raw_data["data"]["Page"]["media"]
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
        payload.link = f"https://anilist.co/{cmd.lower()}/{payload.series_id}"
        payload.title = anime_manga["title"]["english"] or anime_manga["title"]["romaji"] or "No Title"
        payload.description = anime_manga.get("description", None)
        payload.next_episode_time = anilist_get_next_episode_time(anime_manga)
        payload.next_episode_int = anilist_get_next_episode_int(anime_manga)
        payload.image = anilist_get_image_banner(anime_manga)
        payload.embed_description = description_parser(payload.description)
        payload.studios = anilist_get_studios(anime_manga)
        payload.external_links = anilist_get_external_links(anime_manga)
        payload.info_format = anilist_get_format(anime_manga.get("format", cmd), anilist_get_country_of_origin(anime_manga))
        payload.info_status = "Status: "+str(anime_manga.get("status", None)).lower().replace("_", " ").capitalize()
        payload.info_epschaps = anilist_get_info_episodes_chapters(anime_manga, cmd)
        payload.info_start_end = anilist_get_info_start_end(anime_manga)
        payload.info_start_year = anilist_get_info_start_year(anime_manga)
        payload.info_links = anilist_get_info_links(anime_manga, payload.link, cmd)
        payload.info = "\n".join(filter(None, [payload.info_epschaps, payload.info_links]))
        payload.country_of_origin = anilist_get_country_of_origin(anime_manga)
        payload.country_of_origin_flag_str = get_country_of_origin_flag_str(str(payload.country_of_origin).lower(), force=True)
        payload.relations = anilist_get_relations(anime_manga, cmd)
        payload.names = anilist_get_names(anime_manga)
        payload.tags = anilist_get_tags(anime_manga, hideSpoilers=(not isDiscord), discordSpoilers=isDiscord)

        if anime_manga.get("isAdult", None) == True:
            embeds_adult.append(payload.__dict__)
        else:
            embeds.append(payload.__dict__)
    return (embeds+embeds_adult, data)

def anilist_get_link(id, media_type):
    id = str(id)
    media_type = str(media_type).lower()
    return f"https://anilist.co/{media_type.lower()}/{id}"

def anilist_get_country_of_origin(media_result):
    return media_result.get("countryOfOrigin", None)

def anilist_get_external_links(media_result):
    external_links = ""
    for i in range(0, len(media_result["externalLinks"])):
        ext_link = media_result["externalLinks"][i]
        external_links += f"[{ext_link['site']}]({format_url_encode(ext_link['url'], format_all=True, safe=':/')}), "
        if i + 1 == len(media_result["externalLinks"]):
            external_links = external_links[:-2]
    if len(external_links) > 0:
        return external_links
    else:
        return None

def anilist_get_format(series_format, country_of_origin: str=""):
    return format_manga_type(series_format, country_of_origin)

def anilist_get_image_banner(media_result):
    if media_result.get("bannerImage", None):
        return media_result.get("bannerImage", None)
    amid = media_result.get("id", 0)
    return f"https://img.anili.st/media/{amid}"

def anilist_get_info_episodes_chapters(media_result, cmd):
    if cmd == "ANIME" and media_result.get("episodes", None) not in [None, "None"]:
        return "Episodes: "+str(media_result.get("episodes", None))
    if cmd == "MANGA" and media_result.get("chapters", None) not in [None, "None"]:
        return "Chapters: "+str(media_result.get("chapters", None))
    return None

def anilist_get_info_links(media_result, link, cmd):
    info_links = ""
    if media_result.get("isAdult", None) == True:
        info_links += "🔞 "
    info_links += f"[Anilist]({link})"
    if media_result.get("idMal", None):
        info_links += f", [MAL](https://myanimelist.net/{cmd.lower()}/{media_result.get('idMal', None)})"
    if len(info_links) > 0:
        return info_links
    else:
        return None

def anilist_get_info_start_end(media_result):
    info_start = None
    if media_result["startDate"].get("year", None):
        info_start = f"▶️ {media_result['startDate'].get('year', 'YYYY')}-{media_result['startDate'].get('month', 'MM')}-{media_result['startDate'].get('day', 'DD')}"
    info_end = None
    if media_result["endDate"].get("year", None):
        info_end = f"⏹️ {media_result['endDate'].get('year', 'YYYY')}-{media_result['endDate'].get('month', 'MM')}-{media_result['endDate'].get('day', 'DD')}"
    info_start_end = "\n".join(filter(None, [info_start]))
    if info_start_end:
        return info_start_end
    else:
        return None

def anilist_get_info_start_year(media_result):
    info_start_year = media_result["startDate"].get('year', None)
    if info_start_year:
        return str(info_start_year)
    else:
        return None

def anilist_get_names(media_result):
    am_name_native = []
    am_name_native.append(media_result['title'].get('native', None))
    am_name_native.append(media_result['title'].get('romaji', None))
    am_name_native_final = list(filter(None, am_name_native))
    if len(am_name_native_final) <= 0:
        return None
    return am_name_native_final

def anilist_get_next_airing_episode(media_result):
    if media_result.get("nextAiringEpisode"):
        seconds = media_result["nextAiringEpisode"]["timeUntilAiring"]
        return "Next episode in "+str(datetime.timedelta(seconds=seconds))
    else:
        return None

def anilist_get_next_episode_time(media_result):
    if media_result.get("nextAiringEpisode"):
        return media_result["nextAiringEpisode"].get("airingAt", None)
    return None

def anilist_get_next_episode_int(media_result):
    if media_result.get("nextAiringEpisode"):
        return media_result["nextAiringEpisode"].get("episode", None)
    return None

def anilist_get_relations(media_result, cmd):
    relations = []
    relations_raw = anilist_get_relations_raw(media_result, cmd)
    if relations_raw:
        for rel in relations_raw:
            relations.append(f"[{rel.get('series_format')}]({rel.get('link', 'https://anilist.co')})")
    if relations:
        return relations
    else:
        return None

def anilist_get_relations_raw(media_result, media_type: str):
    relations_raw = media_result.get("relations", None)
    if relations_raw is None:
        return None
    relations_node = relations_raw.get("nodes", [])
    if len(relations_node) <= 0:
        return None
    relations = []
    for rel in relations_node:
        link = anilist_get_link(rel.get("id"), media_type)
        series_format = anilist_get_format(rel.get("format", "N/A"), rel.get("countryOfOrigin", None))
        relations.append({
            "link": link,
            "series_format": series_format
        })
    return relations

def anilist_get_studios(media_result):
    studios_count = 0
    if len(media_result["studios"].get("edges", [])) > 0:
        studios_full_arr = media_result["studios"].get("edges", [])
        studios_main_arr = [
            "["+str(stu["node"].get("name", "-"))+"]("+str(stu["node"].get("siteUrl", media_result.get("id", None)))+")"
            for stu in studios_full_arr if stu.get("isMain", None) == True
        ]
        studios_count = len(studios_full_arr) - len(studios_main_arr)
        if len(studios_main_arr) > 0 and studios_count > 1:
            return ", ".join(studios_main_arr)+" + "+str(studios_count)+" others"
        elif len(studios_main_arr) > 0 and studios_count > 0:
            return ", ".join(studios_main_arr)+" + "+str(studios_count)+" other"
        elif len(studios_main_arr) > 0:
            return ", ".join(studios_main_arr)
    return None

def anilist_get_tags(media_result, hideSpoilers=False, discordSpoilers=True):
    genres = media_result.get("genres", [])
    tags = media_result.get("tags", [])
    return_tags = []
    if len(genres) > 0:
        return_tags = [f"**{str(g)}**" for g in genres]
    if len(tags) > 0:
        am_tags_clean = [str(t.get("name", None)) for t in media_result.get("tags", []) if t.get("isMediaSpoiler", None) is not True]
        am_tags_spoilers = [str(t.get("name", None)) for t in media_result.get("tags", []) if t.get("isMediaSpoiler", None) is True]
        am_tags_spoilers_discord = ["||"+str(t.get("name", None))+"||" for t in media_result.get("tags", []) if t.get("isMediaSpoiler", None) is True]

        if hideSpoilers is False and discordSpoilers is True:
            return_tags = return_tags + am_tags_clean + am_tags_spoilers_discord
        elif hideSpoilers is False and discordSpoilers is False:
            return_tags = return_tags + am_tags_clean + am_tags_spoilers
        elif hideSpoilers is True:
            return_tags = return_tags + am_tags_clean
    return return_tags
