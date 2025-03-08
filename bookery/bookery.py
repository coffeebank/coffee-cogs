from redbot.core import Config, app_commands, commands, checks
from redbot.core.utils.views import SimpleMenu
import urllib.parse
import discord
import asyncio
import aiohttp
import json

from .utils_bookery import *
from .utils_discord import *

class Bookery(commands.Cog):
    """Search books and find more about a book. Results from Google Books API."""

    def __init__(self, bot):
        self.config = Config.get_conf(self, identifier=806715409318936616)
        self.bot = bot

    # This cog does not store any End User Data
    async def red_get_data_for_user(self, *, user_id: int):
        return {}
    async def red_delete_data_for_user(self, *, requester, user_id: int) -> None:
        pass


    @commands.hybrid_command(name="book", aliases=["bookery"])
    @commands.has_permissions(embed_links=True)
    @app_commands.describe(text="Search books and find more about a book")
    async def bookery(self, ctx, *, text):
        """Search books and find more about a book.
        
        Results from Google Books API.
        """
        results = await fetch_google_books(text)
        if results in [None, False]:
            return await ctx.send("No results")

        results_max = results.get("items", [])[:10]
        embeds = []
        for res in results_max:
            embeds.append(embed_google_books(res, (await self.bot.get_embed_colour(self))))
        return await SimpleMenu(pages=embeds, timeout=90).start(ctx)
