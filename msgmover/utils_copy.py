import discord

from .utils import *

import logging
logger = logging.getLogger(__name__)


async def timestampEmbed(self, ctx, utcTimeObj):
    embedColor = await ctx.embed_colour()
    embed = discord.Embed(color=embedColor, timestamp=utcTimeObj)
    embed.set_footer(text='\u200b')
    return embed
