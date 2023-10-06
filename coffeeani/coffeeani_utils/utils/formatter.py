# Parts of this file contains code from:
# Jintaku, Wyn: AGPL-3.0 License

import re
import urllib.parse

from .constants import LANGUAGE_FLAGS_MAP

def format_manga_type(series_format, country_of_origin: str=""):
    if series_format in [None, True, False, []]:
        return series_format
    series_format = str(series_format).replace("_", " ")
    if country_of_origin:
        if country_of_origin.lower() in ["kr", "ko"] and series_format.lower() == "manga":
            return "MANHWA"
        if country_of_origin.lower().split("-")[0] in ["zh", "cn"] and series_format.lower() in ["anime", "ona"]:
            return "DONGHUA"
        if country_of_origin.lower().split("-")[0] in ["zh", "cn"] and series_format.lower() == "manga":
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

def format_translate(text: str, source_lang: str="a", target_lang: str="en"):
    if text is None:
        return None
    encoded_text = format_url_encode(text)
    translate = f"https://www.deepl.com/translator#{source_lang}/{target_lang}/{encoded_text}"
    return translate

def format_url_encode(text: str):
    if text is None:
        return None
    east_asian_chars = (
        '\u4E00-\u9FFF'  # Common Hanzi/Kanji characters
        '|\u3400-\u4DBF'  # Extension A for rare Hanzi/Kanji characters
        '|\uF900-\uFAFF'  # Compatibility Ideographs
        '|\u3040-\u309F'  # Hiragana
        '|\u30A0-\u30FF'  # Katakana
        '|\uFF65-\uFF9F'  # Half-width Katakana
        '|\u1100-\u11FF'  # Hangul Jamo
        '|\u3130-\u318F'  # Hangul Compatibility Jamo
        '|\uA960-\uA97F'  # Hangul Jamo Extended-A
        '|\uAC00-\uD7AF'  # Hangul Syllables
        '|\uD7B0-\uD7FF'  # Hangul Jamo Extended-B
    )
    # Use regex sub to replace all non-East Asian characters with their quoted versions
    return re.sub(f'[^{east_asian_chars}]', lambda m: urllib.parse.quote(m.group(0)), text)

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
    if LANGUAGE_FLAGS_MAP.get(str(language_code).lower().replace('_', '-'), None):
        return f":flag_{LANGUAGE_FLAGS_MAP.get(str(language_code).lower().replace('_', '-'), None)}: "
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

def description_parser(description, limit_lines: int=5, limit_char: int=550, flatten_lines: bool=False):
    if description is None:
        return None
    description = clean_spoilers(description)
    description = clean_html(description)
    if limit_lines:
        description = "\n".join(description.split("\n")[:limit_lines])
    if flatten_lines:
        description = description.replace("\n", " ").replace("\r", " ")
    if limit_char and len(description) > limit_char:
        return description[:limit_char] + "..."
    else:
        return description

def list_maximum(items):  # Limits to 5 strings than adds "+X more"
    if len(items) > 5:
        return items[:5] + ["+ " + str(len(items) - 5) + " more"]
    else:
        return items
