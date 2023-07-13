import aiohttp
import asyncio
import discord
import json

from .utils import *

def embed_google_books(book_result, embed_colour: discord.Colour=None):
    book_info = book_result.get("volumeInfo", None)
    title = to_str(book_info.get("title", None))
    subtitle = to_str(book_info.get("subtitle", None))
    if subtitle:
        subtitle = "***"+subtitle+"***\n"
    description = to_str(book_info.get("description", None))
    if description:
        description = truncate(description, 4096)
    info_link = to_str(book_info.get("infoLink", None))
    authors = ", ".join(book_info.get("authors", []))
    publisher = to_str(book_info.get("publisher", None))
    published_date = to_str(book_info.get("publishedDate", None))
    page_count = book_info.get("pageCount", None)
    if page_count and page_count <= 0:
        page_count = None
    else:
        page_count = to_str(page_count)
    categories = ", ".join(book_info.get("categories", []))
    maturity_rating = book_info.get("maturityRating", None)
    if maturity_rating == "NOT_MATURE":
        maturity_rating = None

    thumbnail = book_info.get("imageLinks", None)
    if thumbnail:
        try:
            thumbnail = thumbnail.get("thumbnail", None)
        except AttributeError:
            thumbnail = thumbnail.get(next(iter(thumbnail)), None)

    e = discord.Embed(title=title, url=info_link, colour=embed_colour, description="\n".join(filter(None, [
        subtitle,
        description
    ])))
    if authors:
        e.add_field(name="Author(s)", value=authors, inline=True)
    if publisher:
        e.add_field(name="Publisher", value=publisher, inline=True)
    if published_date:
        e.add_field(name="Published", value=published_date, inline=True)
    if categories:
        e.add_field(name="Categories", value=categories, inline=True)
    if page_count:
        e.add_field(name="Pages", value=page_count, inline=True)
    if maturity_rating:
        e.add_field(name="Age Rating", value=maturity_rating, inline=True)
    e.set_thumbnail(url=thumbnail)

    return e
