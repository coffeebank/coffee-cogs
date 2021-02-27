# Standard Imports
import asyncio
import re
import json

# Discord Imports
import discord

# Redbot Imports
from redbot.core import commands, checks, utils, Config
from redbot.core.utils import chat_formatting
from redbot.core.utils.chat_formatting import box, escape

CODE_BLOCK_RE = re.compile(r"^((```.*)(?=\s)|(```))")
ERROR_PATTERN = re.compile(r'\ntest\.dmb.\S.(\d*)\s(error)')
WARNING_PATTERN = re.compile(r'\ntest\.dmb.\S.\d*\serrors,\s(\d*).(warning.)')
INCLUDE_PATTERN = re.compile(r'#(|\W+)include')

BaseCog = getattr(commands, "Cog", object)

# imports and template are from Crossedfall/crossed-cogs and Red bot, many thanks! (no affiliation)


class dmreply(BaseCog):
    def __init__(self, bot):
        
        self.bot = bot
        self.repo_tags = []
        self.config = Config.get_conf(self, identifier=806715409318936616)

        default_guild = {
            "title": "DM from Bot Owner"
        }
        self.config.register_guild(**default_guild)


    @commands.command()
    async def dmreply(self, ctx, user_id: int, *, message: str):
        """Sends a DM to a user."""

        destination = self.bot.get_user(user_id)
        if destination is None or destination.bot:
            await ctx.send("Invalid ID, user not found, or user is a bot.")
            return

        description = await self.config.guild(ctx.guild).title()
        # content = _("You can reply to this message with {}contact").format(prefix)
        if await ctx.embed_requested():
            e = discord.Embed(colour=discord.Colour.red(), description=message)

            # e.set_footer(text=content)
            if ctx.bot.user.avatar_url:
                e.set_author(name=description, icon_url=ctx.bot.user.avatar_url)
            else:
                e.set_author(name=description)

            try:
                await destination.send(embed=e)
            except discord.HTTPException:
                await ctx.send("Sorry, I couldn't deliver your message")
            else:
                await ctx.send("Message delivered")
        else:
            response = "{}\nMessage:\n\n{}".format(description, message)
            try:
                await destination.send("{}\n{}".format(box(response)))
            except discord.HTTPException:
                await ctx.send("Sorry, I couldn't deliver your message")
            else:
                await ctx.send("Message delivered")


    @commands.command()
    @checks.admin_or_permissions(manage_guild=True)
    async def setdmreply(self, ctx, setting="", *, message):
        """Change the configurations in dmreply
        
        - title
        """
        if setting == "title":
            await self.config.guild(ctx.guild).title.set(message)
            await ctx.message.add_reaction("✅")
        else:
            title = await self.config.guild(ctx.guild).title()
            await ctx.send(title)
