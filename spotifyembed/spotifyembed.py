# from redbot.core import Config
from redbot.core import Config, commands, checks
import asyncio
import aiohttp
import discord
from discord import Webhook, AsyncWebhookAdapter
import re

class Spotifyembed(commands.Cog):
    """Automatically send a reply to Spotify links with a link to the embed preview. Convenient for mobile users who can finally listen to music samples from Discord, without needing an account."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=806715409318936616)
        default_guild = {
            "spotifyembedEnabled": False,
        }
        self.config.register_guild(**default_guild)


    @commands.group(aliases=["setspembed", "setspe"])
    @checks.guildowner_or_permissions()
    async def setspotifyembed(self, ctx: commands.Context):
        """Set Spotify Embed settings"""
        if not ctx.invoked_subcommand:
            # Guild settings
            e = discord.Embed(color=(await ctx.embed_colour()), title="Guild Settings", description="")
            e.add_field(name="spotifyembedEnabled", value=(await self.config.guild(ctx.guild).spotifyembedEnabled()), inline=False)
            await ctx.send(embed=e)

    @setspotifyembed.command(name="enable")
    async def setspembedenable(self, ctx):
        """Enable auto-responding to Spotify links"""
        await self.config.guild(ctx.guild).spotifyembedEnabled.set(True)
        await ctx.message.add_reaction("✅")

    @setspotifyembed.command(name="disable")
    async def setspembeddisable(self, ctx):
        """Disable auto-responding to Spotify links"""
        await self.config.guild(ctx.guild).spotifyembedEnabled.set(False)
        await ctx.message.add_reaction("✅")

    @commands.command(aliases=["spembed", "spe"])
    async def spotifyembed(self, ctx, spotifyLink, asMyself: bool=False):
        """Return a Spotify embed link
        
        Can set asMyself to true/false, for sending as webhook"""
        spembedSplit = spotifyLink.split('.com/')
        sendMsg = spembedSplit[0] + ".com/embed/" + spembedSplit[1]

        if asMyself == False:
            return await ctx.send(sendMsg)
        elif asMyself == True:
            # Find a webhook that the bot made
            try:
                whooklist = await ctx.channel.webhooks()
                whurl = ""
                # Return if match
                for wh in whooklist:
                    if self.bot.user == wh.user:
                        whurl = wh.url
                # Make new webhook if one didn't exist
                if whurl == "":
                    newHook = await ctx.channel.create_webhook(name="Webhook")
                    whurl = newHook.url

                async with aiohttp.ClientSession() as session:
                    webhook = Webhook.from_url(whurl, adapter=AsyncWebhookAdapter(session))
                    await webhook.send(
                        sendMsg,
                        username=ctx.author.display_name,
                        avatar_url=ctx.author.avatar_url,
                    )
            except discord.errors.Forbidden:
                return await ctx.send(sendMsg)
        else:
            return await ctx.send("An error occurred.")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if message.webhook_id:
            return
        if message.guild is None:
            return
        spotifyembedEnabled = await self.config.guild(message.guild).spotifyembedEnabled()
        if spotifyembedEnabled is not True:
            return
        # Ignore if we find [p]spotifyembed in the trigger message
        spembedCommandIgnore = r"^\S{1,9}(spotifyembed|spembed|spe)(?=\s|$)"
        spembedCommands = re.findall(spembedCommandIgnore, message.clean_content)
        if len(spembedCommands) > 0:
            return
        # Ignore if we find no spotify links in the trigger message
        spembedFinder = r"https\:\/\/open\.spotify\.com\/\w{4,12}\/\w{14,26}(?=\?|$|\s)"
        spembedMatches = re.findall(spembedFinder, message.clean_content)
        if len(spembedMatches) <= 0:
            return

        sendMsg = ""

        for match in spembedMatches:
            spembedSplit = match.split('.com/')
            sendMsg += spembedSplit[0] + ".com/embed/" + spembedSplit[1] + "\n"

        # Find a webhook that the bot made
        try:
            whooklist = await message.channel.webhooks()
            whurl = ""
            # Return if match
            for wh in whooklist:
                if self.bot.user == wh.user:
                    whurl = wh.url
            # Make new webhook if one didn't exist
            if whurl == "":
                newHook = await message.channel.create_webhook(name="Webhook")
                whurl = newHook.url

            async with aiohttp.ClientSession() as session:
                webhook = Webhook.from_url(whurl, adapter=AsyncWebhookAdapter(session))
                await webhook.send(
                    sendMsg,
                    username=message.author.display_name,
                    avatar_url=message.author.avatar_url,
                )
        except discord.errors.Forbidden:
            return await message.channel.send(sendMsg)
