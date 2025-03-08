import aiohttp
import asyncio
import json

import logging
logger = logging.getLogger(__name__)

async def fetch_url(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                logger.error(f"Failed to fetch {url}. Status code: {resp.status}")
                return None
            try:
                reqdata = await resp.json()
                return reqdata
            except aiohttp.ClientError as e:
                logger.error(f"An error occurred while parsing JSON: {e}")
                return None

async def fetch_google_books(text):
    try:
        resp = await fetch_url(f"https://www.googleapis.com/books/v1/volumes?q={text}")
        if resp.get("totalItems", 0) > 0:
            return resp
        else:
            return False
    except Exception as e:
        logger.error(f"Failed to fetch results for {text}. Error: {e}")
        return None
