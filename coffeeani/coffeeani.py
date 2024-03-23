from redbot.core import Config, app_commands, commands, checks
import asyncio
import discord

from .coffeeani_utils import *
from .models import ExtendedSimpleMenu

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
        """Search for anime, animations, and donghua
        """
        # TODO: Add MyAnimeList Support
        # Searches Anilist.
        
        # To search by source, use:
        # - `[p]anilist anime`
        # """
        msg = await ctx.send(embeds=[discord_embed_source(NAME_ANILIST, COLOR_ANILIST)])
        embeds = await discord_anilist_embeds(ctx, "ANIME", title)
        if embeds:
            return await ExtendedSimpleMenu(pages=embeds, timeout=90).replace(ctx, msg)
        return await msg.edit(embeds=[discord_embed_source(None)])

    @commands.hybrid_command(aliases=["manhwa", "manhua", "lightnovel"])
    @app_commands.describe(title="Search for manga/manhwa/manhua and light novels")
    @commands.bot_has_permissions(embed_links=True, add_reactions=True)
    async def manga(self, ctx, *, title):
        """Search for manga, manhwa, manhua, and light novels
        
        Searches Anilist, MangaDex, and Batoto.

        To search by source, use:
        - `[p]anilist manga`
        - `[p]batoto`
        - `[p]mangadex`
        """
        msg = await ctx.send(embeds=[discord_embed_source(NAME_ANILIST, COLOR_ANILIST)])
        embeds = await discord_anilist_embeds(ctx, "MANGA", title)
        if embeds:
            return await ExtendedSimpleMenu(pages=embeds, timeout=90).replace(ctx, msg)

        await msg.edit(embeds=[discord_embed_source(NAME_MANGADEX, COLOR_MANGADEX)])
        embeds = await discord_mangadex_embeds(title)
        if embeds:
            return await ExtendedSimpleMenu(pages=embeds, timeout=90).replace(ctx, msg)

        await msg.edit(embeds=[discord_embed_source(NAME_BATOTO, COLOR_BATOTO)])
        embeds = await discord_batoto_embeds(title)
        if embeds:
            return await ExtendedSimpleMenu(pages=embeds, timeout=90).replace(ctx, msg)

        return await msg.edit(embeds=[discord_embed_source(None)])

    @commands.hybrid_command(name="animecharacter", aliases=["animechar"])
    @app_commands.describe(name="Search for an anime/manga character")
    async def character(self, ctx, *, name):
        """Search for an anime/manga character
        
        Searches Anilist.
        """
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

    @anilist.command(name="anime", aliases=["donghua"])
    @app_commands.describe(title="Search Anilist for anime")
    async def anilist_anime(self, ctx, *, title):
        """Search Anilist for anime"""
        msg = await ctx.send(embeds=[discord_embed_source(NAME_ANILIST, COLOR_ANILIST)])
        embeds = await discord_anilist_embeds(ctx, "ANIME", title)
        if embeds:
            return await ExtendedSimpleMenu(pages=embeds, timeout=90).replace(ctx, msg)
        return await msg.edit(embeds=[discord_embed_source(None)])

    @anilist.command(name="manga", aliases=["manhwa", "manhua", "lightnovel"])
    @app_commands.describe(title="Search Anilist for manga/manhwa/manhua and light novels")
    async def anilist_manga(self, ctx, *, title):
        """Search Anilist for manga, manhwa, manhua, and light novels"""
        msg = await ctx.send(embeds=[discord_embed_source(NAME_ANILIST, COLOR_ANILIST)])
        embeds = await discord_anilist_embeds(ctx, "MANGA", title)
        if embeds:
            return await ExtendedSimpleMenu(pages=embeds, timeout=90).replace(ctx, msg)
        return await msg.edit(embeds=[discord_embed_source(None)])

    @anilist.command(name="user")
    @app_commands.describe(username="Search Anilist for a user")
    async def anilist_user(self, ctx, *, username: str):
        """Search Anilist for a user"""
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
        msg = await ctx.send(embeds=[discord_embed_source(NAME_MANGADEX, COLOR_MANGADEX)])
        embeds = await discord_mangadex_embeds(title)
        if embeds:
            return await ExtendedSimpleMenu(pages=embeds, timeout=90).replace(ctx, msg)
        return await msg.edit(embeds=[discord_embed_source(None)])

    @commands.hybrid_command()
    @app_commands.describe(title="Search Batoto for manga, manhwa, and manhua")
    @commands.bot_has_permissions(embed_links=True, add_reactions=True)
    async def batoto(self, ctx, *, title):
        """Search Batoto
        
        Search Batoto for manga, manhwa, and manhua"""
        msg = await ctx.send(embeds=[discord_embed_source(NAME_BATOTO, COLOR_BATOTO)])
        embeds = await discord_batoto_embeds(title)
        if embeds:
            return await ExtendedSimpleMenu(pages=embeds, timeout=90).replace(ctx, msg)
        return await msg.edit(embeds=[discord_embed_source(None)])
