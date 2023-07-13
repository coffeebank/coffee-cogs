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

def anilist_get_format(series_format, country_of_origin: str=""):
    if series_format in [None, True, False, []]:
        return series_format
    series_format = str(series_format).replace("_", " ")
    if country_of_origin == "KR" and series_format == "MANGA":
        return "MANHWA"
    if country_of_origin == "CN" and series_format == "MANGA":
        return "MANHUA"
    return series_format

def anilist_get_relations(media_result, media_type: str):
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
