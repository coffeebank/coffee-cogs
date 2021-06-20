# from redbot.core import Config
from redbot.core import Config, commands, checks
import asyncio
import aiohttp
import discord
from discord import Webhook, AsyncWebhookAdapter
import re

class Playsoju(commands.Cog):
    """Automatically send replies to Spotify links with Soju Player links, for mobile users"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=806715409318936616)
        default_guild = {
            "sojuEnabled": True,
            "sojuInstance": "playsoju.netlify.app",
            "sojuOptions": "&sa=true"
        }
        self.config.register_guild(**default_guild)


    @commands.group()
    @checks.guildowner_or_permissions()
    async def setsoju(self, ctx: commands.Context):
        """Set Soju Player settings"""
        if not ctx.invoked_subcommand:
            # Global settings
            e = discord.Embed(color=(await ctx.embed_colour()), title="Guild Settings", description="")
            e.add_field(name="sojuEnabled", value=(await self.config.guild(ctx.guild).sojuEnabled()), inline=False)
            e.add_field(name="sojuInstance", value=(await self.config.guild(ctx.guild).sojuInstance()), inline=False)
            e.add_field(name="sojuOptions", value=(await self.config.guild(ctx.guild).sojuOptions()), inline=False)
            await ctx.send(embed=e)

    @setsoju.command(name="enable")
    async def setsojuenable(self, ctx):
        """Enable Soju Player"""
        await self.config.guild(ctx.guild).sojuEnabled.set(True)
        await ctx.message.add_reaction("✅")

    @setsoju.command(name="disable")
    async def setsojudisable(self, ctx):
        """Disable Soju Player"""
        await self.config.guild(ctx.guild).sojuEnabled.set(False)
        await ctx.message.add_reaction("✅")

    @setsoju.command(name="instance")
    async def setsojuinstance(self, ctx, instanceDomain):
        """Set Soju Player instance
        
        Default: playsoju.netlify.app"""
        await self.config.guild(ctx.guild).sojuInstance.set(instanceDomain)
        await ctx.message.add_reaction("✅")

    @setsoju.command(name="options")
    async def setsojuoptions(self, ctx, queryParamString):
        """Set Soju Player query parameters

        Type them all together using &
        
        Default: &sa=true

        [See here for the full list](https://github.com/coffeebank/soju#instances)"""
        await self.config.guild(ctx.guild).sojuOptions.set(queryParamString)
        await ctx.message.add_reaction("✅")

    @commands.command()
    async def playsoju(self, ctx, spotifyLink, asMyself: bool=False):
        """Return a Soju link
        
        Can set asMyself to true/false, for sending as webhook"""
        sojuInstance = await self.config.guild(ctx.guild).sojuInstance()
        sojuOptions = await self.config.guild(ctx.guild).sojuOptions()
        sendMsg = f"https://{sojuInstance}?s={spotifyLink}{sojuOptions}\n"

        if asMyself == False:
            return await ctx.send(sendMsg)
        elif asMyself == True:
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
                return await ctx.channel.send(sendMsg)
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
        sojuEnabled = await self.config.guild(message.guild).sojuEnabled()
        if sojuEnabled is not True:
            return
        sojuFinder = r"https\:\/\/open\.spotify\.com\/\w{4,12}\/\w{14,26}(?=\?|$)"
        matches = re.findall(sojuFinder, message.clean_content)
        if len(matches) <= 0:
            return

        sojuInstance = await self.config.guild(message.guild).sojuInstance()
        sojuOptions = await self.config.guild(message.guild).sojuOptions()
        sendMsg = ""

        for match in matches:
            sendMsg += "https://"+sojuInstance+"?s="+match+sojuOptions+"\n"

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

