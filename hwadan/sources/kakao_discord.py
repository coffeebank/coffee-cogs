import discord

import io
from typing import List

from .kakao import COLOR_KAKAO, kakao_search_manga
from ..utils import embed_result, description_parser, translate_deepl

import logging
logger = logging.getLogger(__name__)

async def discord_kakao_embeds(self, entered_title):
    results = await kakao_search_manga(entered_title)
    if not results:
        logger.debug(f'No results for: {str(entered_title)}', exc_info=True)
        return None
    embed_data, data = results

    embeds = []
    idx_total = len(embed_data)
    for idx, em in enumerate(embed_data):
        romanized_title = em.get('romanized_title')
        translated_title = await translate_deepl(self, em.get('title'), "KO", "EN")
        if romanized_title:
            em['title'] = em['title'] + f' ({str(romanized_title)})'
            em['names'].append(str(romanized_title))
        if translated_title:
            em['names'] = [str(translated_title).title()]
        translated_description = await translate_deepl(self, em.get('description'), "KO", "EN")
        translated_embed_description = description_parser(translated_description, limit_lines=False, flatten_lines=True)
        if translated_embed_description:
            em['embed_description'] = translated_embed_description
        embed = embed_result(em, COLOR_KAKAO)
        embed.insert_field_at(1, name="Creators", value=em.get('authors'), inline=True)
        embed.set_footer(text=" ・ ".join(filter(None, [" ".join(filter(None, [em["info_format"], em["info_start_year"]])), "Results from Kakao Webtoon (카카오웹툰)", str(idx+1)+"/"+str(idx_total)])))
        embeds.append({"embed": embed})
    return embeds

def discord_kakao_generate_image_banner(files_list: List, embed, em_result, idx: int, image: io.BytesIO):
    files = files_list
    file_obj = discord.File(fp=em_result.get("image", None), filename="kakao-webtoon-"+str(idx+1)+".webp")
    files.append(file_obj)
    embed.set_image(url="attachment://kakao-webtoon-"+str(idx+1)+".webp")
    return (files_list, embed)
