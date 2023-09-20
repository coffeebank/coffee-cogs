from redbot.core import Config, app_commands, commands, checks
import asyncio
import discord

from .models import *
from .sources import *
from .utils import *

import logging
logger = logging.getLogger(__name__)

class Coffeeani(commands.Cog):
    """Search for anime, manga, manhwa/manhua, light novels, and characters. See series info, status, episodes/chapters, and tags."""

    def __init__(self, bot):
        self.bot = bot

    async def red_delete_data_for_user(self, **kwargs):
        """Nothing to delete."""
        return

    @commands.hybrid_command()
    @app_commands.describe(title="Search for anime")
    @commands.bot_has_permissions(embed_links=True, add_reactions=True)
    async def anime(self, ctx, *, title):
        """Searches for anime using Anilist"""
        msg = await ctx.send(embeds=[embed_source("Anilist", COLOR_ANILIST)])
        embeds = await discord_anilist_embeds(ctx, "ANIME", title)
        if embeds:
            return await ExtendedSimpleMenu(pages=embeds, timeout=90).replace(ctx, msg)
        return await msg.edit(embeds=[embed_source(None)])

    @commands.hybrid_command(aliases=["manhwa", "만화", "manhua", "漫画", "lightnovel"])
    @app_commands.describe(title="Search for manga/manhwa/manhua and light novels")
    @commands.bot_has_permissions(embed_links=True, add_reactions=True)
    async def manga(self, ctx, *, title):
        """Searches for manga, manhwa, manhua, and light novels
        
        Searches AniList, MangaDex, and Batoto.
        
        To search AniList only, use the  **`[p]anilist manga`**  command.
        To search MangaDex only, use the  **`[p]mangadex`**  command.
        To search Batoto only, use the  **`[p]batoto`**  command.
        To search Kakao Webtoon only, use the  **`[p]kakao`**  command.
        """
        msg = await ctx.send(embeds=[embed_source("Anilist", COLOR_ANILIST)])
        embeds = await discord_anilist_embeds(ctx, "MANGA", title)
        if embeds:
            return await ExtendedSimpleMenu(pages=embeds, timeout=90).replace(ctx, msg)

        await msg.edit(embeds=[embed_source("MangaDex", COLOR_MANGADEX)])
        embeds = await discord_mangadex_embeds(title)
        if embeds:
            return await ExtendedSimpleMenu(pages=embeds, timeout=90).replace(ctx, msg)

        await msg.edit(embeds=[embed_source("Batoto", COLOR_BATOTO)])
        embeds = await discord_batoto_embeds(title)
        if embeds:
            return await ExtendedSimpleMenu(pages=embeds, timeout=90).replace(ctx, msg)

        return await msg.edit(embeds=[embed_source(None)])

    @commands.hybrid_command(name="animecharacter", aliases=["animechar"])
    @app_commands.describe(name="Search for an anime/manga character")
    async def character(self, ctx, *, name):
        """Searches for characters using Anilist"""
        entered_title = name

        try:
            embeds, data = await discord_anilist_search_character(ctx, entered_title)

            if embeds is not None:
                await ExtendedSimpleMenu(pages=embeds, timeout=90).start(ctx)
            else:
                await ctx.send("No characters were found or there was an error in the process")

        except TypeError:
            await ctx.send("No characters were found or there was an error in the process")

    @commands.hybrid_group(name="anilist")
    async def anilist(self, ctx: commands.Context):
        """Search Anilist"""
        if not ctx.invoked_subcommand:
            pass

    @anilist.command(name="manga", aliases=["manhwa", "만화", "manhua", "漫画", "lightnovel"])
    @app_commands.describe(title="Search AniList for manga/manhwa/manhua and light novels")
    async def anilist_manga(self, ctx, *, title):
        """Searches for manga, manhwa, manhua, and light novels using Anilist"""
        msg = await ctx.send(embeds=[embed_source("Anilist", COLOR_ANILIST)])
        embeds = await discord_anilist_embeds(ctx, "MANGA", title)
        if embeds:
            return await ExtendedSimpleMenu(pages=embeds, timeout=90).replace(ctx, msg)
        return await msg.edit(embeds=[embed_source(None)])

    @anilist.command(name="user")
    @app_commands.describe(username="Search Anilist for a user")
    async def anilist_user(self, ctx, *, username: str):
        """Searches users using Anilist"""
        entered_title = username

        try:
            embeds, data = await discord_anilist_search_user(ctx, entered_title)

            if embeds is not None:
                await ExtendedSimpleMenu(pages=embeds, timeout=90).start(ctx)
            else:
                await ctx.send("No users were found or there was an error in the process")

        except TypeError:
            await ctx.send("No users were found or there was an error in the process")

    @commands.hybrid_command()
    @app_commands.describe(title="Search MangaDex for manga, manhwa, and manhua")
    @commands.bot_has_permissions(embed_links=True, add_reactions=True)
    async def mangadex(self, ctx, *, title):
        """Search MangaDex
        
        Search MangaDex for manga, manhwa, and manhua"""
        msg = await ctx.send(embeds=[embed_source("MangaDex", COLOR_MANGADEX)])
        embeds = await discord_mangadex_embeds(title)
        if embeds:
            return await ExtendedSimpleMenu(pages=embeds, timeout=90).replace(ctx, msg)
        return await msg.edit(embeds=[embed_source(None)])

    @commands.hybrid_command()
    @app_commands.describe(title="Search Batoto for manga, manhwa, and manhua")
    @commands.bot_has_permissions(embed_links=True, add_reactions=True)
    async def batoto(self, ctx, *, title):
        """Search Batoto
        
        Search Batoto for manga, manhwa, and manhua"""
        msg = await ctx.send(embeds=[embed_source("Batoto", COLOR_BATOTO)])
        embeds = await discord_batoto_embeds(title)
        if embeds:
            return await ExtendedSimpleMenu(pages=embeds, timeout=90).replace(ctx, msg)
        return await msg.edit(embeds=[embed_source(None)])

    @commands.hybrid_command()
    @app_commands.describe(title="Search Kakao for manhwa")
    @commands.bot_has_permissions(embed_links=True, add_reactions=True)
    async def kakao(self, ctx, *, title):
        """Search Kakao
        
        Search Kakao Webtoons for manhwa. Searches are in Korean by default.

        > ✅ 공주
        """
        msg = await ctx.send(embeds=[embed_source("Kakao Webtoon (카카오웹툰)", COLOR_KAKAO)])
        if title.startswith('"') and title.endswith('"') and len(title) > 2:
            title = title[1:-1]
        elif title.isascii():
            translated = await translate_deepl(self, title, "EN", "KO")
            if translated:
                title = translated
        embeds = await discord_kakao_embeds(self, title)
        if embeds:
            return await ExtendedSimpleMenu(pages=embeds, timeout=90).replace(ctx, msg)
        return await msg.edit(embeds=[embed_source(None)])
