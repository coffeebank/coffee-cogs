import discord

from .mangadex import COLOR_MANGADEX, mangadex_search_manga
from ..utils import embed_result

import logging
logger = logging.getLogger(__name__)

async def discord_mangadex_embeds(entered_title):
    results = await mangadex_search_manga(entered_title)
    if not results:
        logger.debug(f'No results for: {str(entered_title)}', exc_info=True)
        return None
    embed_data, data = results

    embeds = []
    idx_total = len(embed_data)
    for idx, em in enumerate(embed_data):
        embed = embed_result(em, COLOR_MANGADEX)
        embed.set_footer(text=" ・ ".join(filter(None, [" ".join(filter(None, [em["info_format"], em["info_start_year"]])), "Results from MangaDex", str(idx+1)+"/"+str(idx_total)])))
        embeds.append({"embed": embed})
    return embeds
