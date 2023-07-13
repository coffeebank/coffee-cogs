import aiohttp
import asyncio
import json


async def fetch_url(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            reqdata = await resp.json()
            return reqdata

async def fetch_google_books(text):
    try:
        resp = await fetch_url(f"https://www.googleapis.com/books/v1/volumes?q={text}")
        if resp.get("totalItems", 0) > 0:
            return resp
        else:
            return False
    except:
        return None
