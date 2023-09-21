import discord

from .batoto import NAME_BATOTO, COLOR_BATOTO, batoto_search_manga
from ..utils import discord_embed_result

import logging
logger = logging.getLogger(__name__)

async def discord_batoto_embeds(entered_title):
    results = await batoto_search_manga(entered_title)
    if not results:
        logger.debug(f'No results for: {str(entered_title)}', exc_info=True)
        return None
    embed_data, data = results

    embeds = []
    idx_total = len(embed_data)
    for idx, em in enumerate(embed_data):
        embed = discord_embed_result(em, COLOR_BATOTO, NAME_BATOTO, idx, idx_total)
        embeds.append({"embed": embed})
    return embeds
