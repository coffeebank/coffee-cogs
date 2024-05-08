import discord

from ..coffeeani_utils.utils import description_parser, truncate_string_at, deepl_fetch_api

import logging
logger = logging.getLogger(__name__)

def discord_embed_result(result, color: str=None, service: str=None, idx: int=None, idx_total: int=None):
    try:
        em = result
        embed = discord.Embed(title=em.get('title', str(None)))
        embed.url = em.get('link', None)
        embed.description = em.get('embed_description')
        embed.set_image(url=em.get('image'))
        embed.set_thumbnail(url=em.get('image_thumbnail'))
        if color:
            embed.color = discord.Colour.from_str(color)
        if em.get('background_color'):
            embed.color = discord.Colour.from_str(em.get('background_color'))
        if em.get('info'):
            embed.add_field(name=str(em.get('info_status')), value=str(em.get('info')), inline=True)
        if em.get('external_links'):
            embed.add_field(name='Links', value=truncate_string_at(em.get('external_links'), 1000, ','), inline=True)
        if em.get('names'):
            names_inline = True
            names_str = description_parser(', '.join(em.get('names', '')))
            if len(names_str) > 170:
                names_inline = False
            embed.add_field(name='Names', value=em.get('country_of_origin_flag_str', '') + names_str, inline=names_inline)
        if em.get('tags'):
            tags_inline = True
            if len(em.get('tags')) > 11:
                tags_inline = False
            embed.add_field(name='Tags', value=truncate_string_at(', '.join(em.get('tags', '')), 1000, ','), inline=tags_inline)
        if service:
            service = f"Results from {str(service)}"
        idx_str = None
        if idx is not None and idx_total is not None:
            idx_str = "/".join([str(idx+1), str(idx_total)])
        embed.set_footer(text=" ・ ".join(filter(None, [" ".join(filter(None, [em["info_format"], em["info_start_year"]])), service, idx_str])))
        return embed
    except Exception as err:
        logger.error(err, exc_info=True)
        return None

def discord_embed_source(source_being_loaded=None, color=None):
    if not source_being_loaded:
        no_results = discord.Embed(description=f"No results found....")
        return no_results
    embed = discord.Embed(description=f"Searching {str(source_being_loaded)}... ⏳")
    if color:
        embed.color = discord.Colour.from_str(color)
    return embed

async def discord_translate_deepl(self, text, source_lang="KO", target_lang="EN"):
    deepl_key_obj = await self.bot.get_shared_api_tokens("deepl")
    deepl_key = deepl_key_obj.get("api_key", None)
    if not deepl_key:
        logger.debug("No DeepL Free Key")
        return None
    j_translated = await deepl_fetch_api(text, deepl_key, source_lang, target_lang)
    try:
        result = j_translated["translations"][0].get("text")
        if result != text:
            return result
        logger.debug("Improperly translated:", j_translated)
    except Exception as err:
        logger.debug(err)
        return None
