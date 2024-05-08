# Parts of this file contains code from:
# Jintaku, Wyn: AGPL-3.0 License

import discord

import datetime

from ...coffeeani_utils.sources.anilist import NAME_ANILIST, COLOR_ANILIST, SEARCH_ANILIST_CHARACTER_QUERY, SEARCH_ANILIST_USER_QUERY, anilist_request, anilist_search_anime_manga
from ...coffeeani_utils.utils import description_parser, format_name, list_maximum
from ..utils import discord_embed_result

import logging
logger = logging.getLogger(__name__)

async def discord_anilist_embeds(ctx, cmd, entered_title):
    results = await anilist_search_anime_manga(cmd, entered_title, isDiscord=True)
    if not results:
        logger.debug(f'No results for: {str(entered_title)}', exc_info=True)
        return None
    embed_data, data = results

    embeds = []
    idx_total = len(embed_data)
    for idx, em in enumerate(embed_data):
        embed = discord_embed_result(em, COLOR_ANILIST, NAME_ANILIST, idx, idx_total)
        if em.get('studios'):
            embed.insert_field_at(1, name='Studios', value=em.get('studios'), inline=True)
        if em.get("next_episode_time") and em.get("next_episode_int") and cmd == "ANIME":
            embed.insert_field_at(1, name="⏱️ Next Episode", value=f"Ep. {str(str(em.get('next_episode_int')))} <t:{str(em.get('next_episode_time'))}:R>\n<t:{str(em.get('next_episode_time'))}:D>")
        embeds.append({"embed": embed})
    return embeds

async def discord_anilist_search_character(ctx, entered_title):
    variables = {"search": entered_title, "page": 1}
    data = (await anilist_request(SEARCH_ANILIST_CHARACTER_QUERY, variables))["data"]["Page"]["characters"]
    if data is not None and len(data) > 0:
        # a list of embeds
        embeds = []
        for character in data:
            # Sets up various variables for Embed
            link = f"https://anilist.co/character/{character['id']}"
            character_anime = [f'[{anime["title"]["userPreferred"]}]({"https://anilist.co/anime/" + str(anime["id"])})' for anime in character["media"]["nodes"] if anime["type"] == "ANIME"]
            character_manga = [f'[{manga["title"]["userPreferred"]}]({"https://anilist.co/manga/" + str(manga["id"])})' for manga in character["media"]["nodes"] if manga["type"] == "MANGA"]
            embed = discord.Embed(title=format_name(character["name"]["first"], character["name"]["last"]))
            embed.url = link
            embed.color = 3447003
            embed.description = description_parser(character["description"])
            embed.set_thumbnail(url=character["image"]["large"])
            if len(character_anime) > 0:
                embed.add_field(name="Anime", value="\n".join(list_maximum(character_anime)))
            if len(character_manga) > 0:
                embed.add_field(name="Manga", value="\n".join(list_maximum(character_manga)))
            embed.set_footer(text="Powered by Anilist")
            embeds.append(embed)
        return embeds, data
    else:
        return None

async def discord_anilist_search_user(ctx, entered_title):
    variables = {"search": entered_title, "page": 1}
    data = (await anilist_request(SEARCH_ANILIST_USER_QUERY, variables))["data"]["Page"]["users"]
    if data is not None and len(data) > 0:
        # a list of embeds
        embeds = []
        for user in data:
            # Sets up various variables for Embed
            link = f"https://anilist.co/user/{user['id']}"
            title = f"[{user['name']}]({link})"
            title = user["name"]
            embed = discord.Embed(title=title)
            embed.url = link
            embed.color = 3447003
            embed.description = description_parser(user["about"])
            embed.set_thumbnail(url=user["avatar"]["large"])
            embed.add_field(name="Watched time", value=datetime.timedelta(minutes=int(user["stats"]["watchedTime"])))
            embed.add_field(name="Chapters read", value=user["stats"].get("chaptersRead", "N/A"))
            for category in "anime", "manga", "characters":
                fav = []
                for node in user["favourites"][category]["nodes"]:
                    url_path = category
                    if category == "characters":
                        name = node["name"]
                        title = format_name(name["first"], name["last"])
                        url_path = "character"  # without the s
                    else:
                        title = node["title"]["userPreferred"]
                    fav.append(f'[{title}](https://anilist.co/{url_path}/{node["id"]})')
                if fav:
                    embed.add_field(name=f"Favorite {category}", value="\n".join(list_maximum(fav)))
            embed.set_footer(text="Powered by Anilist")
            embeds.append(embed)
        return embeds, data
    else:
        return None
