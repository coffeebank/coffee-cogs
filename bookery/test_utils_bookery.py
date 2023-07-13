import pytest

import aiohttp
import asyncio

from .utils_bookery import *

pytest_plugins = ('pytest_asyncio')

@pytest.mark.asyncio
async def test_fetch_url():
    url = "https://www.googleapis.com/books/v1/volumes?q=ifruranjvtlytkmkbxug"
    response = await fetch_url(url)
    expected_response = {
        "kind": "books#volumes",
        "totalItems": 0
    }
    assert response == expected_response

@pytest.mark.asyncio
async def test_fetch_google_books_1():
    response = await fetch_google_books("ifruranjvtlytkmkbxug")
    assert response in [None, False]
@pytest.mark.asyncio
async def test_fetch_google_books_2():
    response = await fetch_google_books("recommend")
    assert response.get("totalItems", 0) > 7600
