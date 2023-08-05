import asyncio
import aiohttp
import datetime
import json
import re

URL = "https://graphql.anilist.co"

SEARCH_ANIME_MANGA_QUERY = """
query ($id: Int, $page: Int, $search: String, $type: MediaType) {
    Page (page: $page, perPage: 10) {
        media (id: $id, search: $search, type: $type) {
            id
            idMal
            description(asHtml: false)
            title {
                english
                romaji
                native
            }
            coverImage {
                medium
                color
            }
            bannerImage
            averageScore
            meanScore
            status
            episodes
            chapters
            volumes
            externalLinks {
                url
                site
            }
            nextAiringEpisode {
                timeUntilAiring
            }
            countryOfOrigin
            format
            synonyms
            tags {
                name
                isMediaSpoiler
            }
            genres
      			studios {
              edges {
                node {
                  name
                  siteUrl
                }
                isMain
              }
      			}
      			relations {
      			  nodes {
                id
                title {
                  romaji
                  english
                  native
                  userPreferred
                }
                format
                season
                seasonYear
                countryOfOrigin
              }
      			}
      			isAdult
        }
    }
}
"""

SEARCH_CHARACTER_QUERY = """
query ($id: Int, $page: Int, $search: String) {
  Page(page: $page, perPage: 10) {
    characters(id: $id, search: $search) {
      id
      description (asHtml: true),
      name {
        first
        last
        native
      }
      image {
        large
      }
      media {
        nodes {
          id
          type
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
"""

SEARCH_USER_QUERY = """
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
        external_links += f"[{ext_link['site']}]({ext_link['url']}), "
        if i + 1 == len(media_result["externalLinks"]):
            external_links = external_links[:-2]
    if len(external_links) > 0:
        return external_links
    else:
        return None

def anilist_get_format(series_format, country_of_origin: str=""):
    if series_format in [None, True, False, []]:
        return series_format
    series_format = str(series_format).replace("_", " ")
    if country_of_origin == "KR" and series_format == "MANGA":
        return "MANHWA"
    if country_of_origin == "CN" and series_format == "MANGA":
        return "MANHUA"
    return series_format

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

def anilist_get_names(media_result):
    am_name_native = []
    am_name_native.append(media_result['title'].get('native', None))
    am_name_native.append(media_result['title'].get('romaji', None))
    return am_name_native

def anilist_get_next_airing_episode(media_result):
    if media_result.get("nextAiringEpisode"):
        seconds = media_result["nextAiringEpisode"]["timeUntilAiring"]
        return "Next episode in "+str(datetime.timedelta(seconds=seconds))
    else:
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
    if len(media_result.get("tags", [])) > 0:
        am_tags_clean = [str(t.get("name", None)) for t in media_result.get("tags", []) if t.get("isMediaSpoiler", None) is not True]
        am_tags_spoilers = [str(t.get("name", None)) for t in media_result.get("tags", []) if t.get("isMediaSpoiler", None) is True]
        am_tags_spoilers_discord = ["||"+str(t.get("name", None))+"||" for t in media_result.get("tags", []) if t.get("isMediaSpoiler", None) is True]

        if hideSpoilers is False and discordSpoilers is True:
            return am_tags_clean + am_tags_spoilers_discord
        elif hideSpoilers is False and discordSpoilers is False:
            return am_tags_clean + am_tags_spoilers
        elif hideSpoilers is True:
            return am_tags_clean
    return None

async def search_anime_manga(cmd, entered_title, isDiscord=False):
    variables = {"search": entered_title, "page": 1, "type": cmd}
    data = (await request(SEARCH_ANIME_MANGA_QUERY, variables))["data"]["Page"]["media"]

    if data is None and len(data) <= 0:
        return None

    embeds = []
    embeds_adult = []
    idx_total = len(data)

    for idx, anime_manga in enumerate(data):
        series_id = anime_manga.get("id", 0)
        link = f"https://anilist.co/{cmd.lower()}/{series_id}"
        title = anime_manga["title"]["english"] or anime_manga["title"]["romaji"] or "No Title"
        description = anime_manga.get("description", None)
        time_left = anilist_get_next_airing_episode(anime_manga)
        image = anilist_get_image_banner(anime_manga)
        embed_description = description_parser(description)
        studios = anilist_get_studios(anime_manga)
        external_links = anilist_get_external_links(anime_manga)
        info_format = anilist_get_format(anime_manga.get("format", cmd), anilist_get_country_of_origin(anime_manga))
        info_status = "Status: "+str(anime_manga.get("status", None)).lower().replace("_", " ").capitalize()
        info_epschaps = anilist_get_info_episodes_chapters(anime_manga, cmd)
        info_links = anilist_get_info_links(anime_manga, link, cmd)
        info = "\n".join(filter(None, [info_epschaps, info_links]))
        country_of_origin = anilist_get_country_of_origin(anime_manga)
        country_of_origin_flag_str = ":flag_"+str(country_of_origin).lower()+": "
        relations = anilist_get_relations(anime_manga, cmd)
        names = anilist_get_names(anime_manga)
        tags = anilist_get_tags(anime_manga, hideSpoilers=(not isDiscord), discordSpoilers=isDiscord)

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
          'info_links': info_links,
          'info': info,
          'country_of_origin': country_of_origin,
          'country_of_origin_flag_str': country_of_origin_flag_str,
          'relations': relations,
          'names': names,
          'tags': tags,
        }

        if anime_manga.get("isAdult", None) == True:
            embeds_adult.append(payload)
        else:
            embeds.append(payload)

    return embeds+embeds_adult, data


# Jintaku, Wyn: AGPL-3.0 License

def format_name(first_name, last_name):  # Combines first_name and last_name and/or shows either of the two
    if first_name and last_name:
        return first_name + " " + last_name
    elif first_name:
        return first_name
    elif last_name:
        return last_name
    else:
        return "No name"

def clean_html(description):  # Removes html tags
    if not description:
        return ""
    cleanr = re.compile("<.*?>")
    cleantext = re.sub(cleanr, "", description)
    return cleantext

def clean_spoilers(description):  # Removes spoilers using the html tag given by AniList
    if not description:
        return ""
    cleanr = re.compile("/<span[^>]*>.*</span>/g")
    cleantext = re.sub(cleanr, "", description)
    return cleantext

def description_parser(description):  # Limits text to characters and 5 lines and adds "..." at the end
    if description is None:
        return None
    description = clean_spoilers(description)
    description = clean_html(description)
    description = "\n".join(description.split("\n")[:5])
    if len(description) > 500:
        return description[:500] + "..."
    else:
        return description

def list_maximum(items):  # Limits to 5 strings than adds "+X more"
    if len(items) > 5:
        return items[:5] + ["+ " + str(len(items) - 5) + " more"]
    else:
        return items

async def request(query, variables=None):

    if variables is None:
        variables = {}

    request_json = {"query": query, "variables": variables}

    headers = {"content-type": "application/json"}

    async with aiohttp.ClientSession() as session:
        async with session.post(URL, data=json.dumps(request_json), headers=headers) as response:
            return await response.json()
