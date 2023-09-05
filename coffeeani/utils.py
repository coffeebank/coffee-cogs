# Parts of this file contains code from:
# Jintaku, Wyn: AGPL-3.0 License

import re
import urllib.parse

LANGUAGE_FLAGS_MAP = {
  "en": "gb",
  "id": "id",
  "ja": "jp",
  "ko": "kr",
  "pt-br": "br",
  "th": "th",
  "tr": "tr",
  "vi": "vn",
  "zh": "cn",
  "zh-cn": "cn",
  "zh-hans": "cn",
  "zh-hans-hk": "hk",
  "zh-hans-tw": "tw",
  "zh-hant": "tw",
  "zh-hant-hk": "hk",
  "zh-hant-tw": "tw",
  "zh-hk": "hk",
  "zh-mo": "mo",
  "zh-sg": "sg",
  "zh-tw": "tw",
}

def format_manga_type(series_format, country_of_origin: str=""):
    if series_format in [None, True, False, []]:
        return series_format
    series_format = str(series_format).replace("_", " ")
    if country_of_origin:
        if country_of_origin.lower() in ["kr", "ko"] and series_format.lower() == "manga":
            return "MANHWA"
        if country_of_origin.lower().split("-")[0] in ["cn", "zh"] and series_format.lower() == "manga":
            return "MANHUA"
    return series_format

def format_name(first_name, last_name):  # Combines first_name and last_name and/or shows either of the two
    if first_name and last_name:
        return first_name + " " + last_name
    elif first_name:
        return first_name
    elif last_name:
        return last_name
    else:
        return "No name"

def format_string(string):
    if string:
        return str(string)
    return None

def format_translate(text: str):
    encoded_text = urllib.parse.quote(text, safe="")
    translate = f"https://www.deepl.com/translator#a/en/{encoded_text}"
    return translate

def get_array_first_key(arr):
    if arr:
        return next(iter(arr))
    return None

def get_joined_array_from_json(json_obj, key: str):
    arr = json_obj.get(key, None)
    if arr:
        return ", ".join(arr)
    return None

def get_country_of_origin_flag_str(language_code: str):
    if LANGUAGE_FLAGS_MAP.get(str(language_code).lower(), None):
        return f":flag_{LANGUAGE_FLAGS_MAP.get(str(language_code).lower(), None)}: "
    else:
        return f"[{str(language_code).upper()}] "

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
    if len(description) > 550:
        return description[:550] + "..."
    else:
        return description

def list_maximum(items):  # Limits to 5 strings than adds "+X more"
    if len(items) > 5:
        return items[:5] + ["+ " + str(len(items) - 5) + " more"]
    else:
        return items
