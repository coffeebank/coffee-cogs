import discord

from ...coffeeani_utils.sources.bangumi import NAME_BANGUMI, COLOR_BANGUMI, bangumi_search_anime_manga
from ..utils import discord_embed_result

import logging
logger = logging.getLogger(__name__)

async def discord_bangumi_embeds(bangumi_type, entered_title):
    results = await bangumi_search_anime_manga(bangumi_type, entered_title)
    if not results:
        logger.debug(f'No results for: {str(entered_title)}', exc_info=True)
        return None
    embed_data, data = results

    embeds = []
    idx_total = len(embed_data)
    for idx, em in enumerate(embed_data):
        embed = discord_embed_result(em, COLOR_BANGUMI, NAME_BANGUMI, idx, idx_total, names_inline=False, tags_inline=False)
        embeds.append({"embed": embed})
    return embeds
