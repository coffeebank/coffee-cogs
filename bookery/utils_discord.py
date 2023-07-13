import aiohttp
import asyncio
import discord
import json

def to_str(obj):
    if obj in [None, True, False, []]:
        return obj
    else:
        return str(obj)

def embed_google_books(book_result, embed_colour: discord.Colour=None):
    book_info = book_result.get("volumeInfo", None)
    title = to_str(book_info.get("title", None))
    subtitle = to_str(book_info.get("subtitle", None))
    info_link = to_str(book_info.get("infoLink", None))
    authors = ", ".join(book_info.get("authors", []))
    published_date = to_str(book_info.get("publishedDate", None))
    page_count = to_str(book_info.get("pageCount", None))
    categories = ", ".join(book_info.get("categories", []))
    maturity_rating = to_str(book_info.get("maturityRating", None))
    if maturity_rating:
        maturity_rating = maturity_rating.replace("_", " ")

    thumbnail = book_info.get("imageLinks", None)
    if thumbnail:
        try:
            thumbnail = thumbnail.get("thumbnail", None)
        except AttributeError:
            thumbnail = thumbnail.get(next(iter(thumbnail)), None)

    e = discord.Embed(title=title, url=info_link, description="\n".join(filter(None, [
        subtitle,
        authors,
        published_date,
        page_count,
        categories,
        maturity_rating
    ])))
    e.set_thumbnail(url=thumbnail)

    return e
