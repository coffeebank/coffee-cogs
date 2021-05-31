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
        }
        self.config.register_guild(**default_guild)

    
    # Utility Commands

    async def webhookFinder(self, ctx, bot):
        # Find a webhook that the bot made
        try:
            whooklist = await ctx.channel.webhooks()
        except:
            return False
        # Return if match
        for wh in whooklist:
            if bot.user == wh.user:
                return wh.url
        # If the function got here, it means there isn't one that the bot made
        try:
            newHook = await ctx.channel.create_webhook(name="Playsoju")
            return newHook.url
        # Could not create webhook, return False
        except:
            return False

    async def webhookSender(self, message, webhookUrl, sendMsg):
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(webhookUrl, adapter=AsyncWebhookAdapter(session))
        try:
            await webhook.send(
                sendMsg,
                username=message.author.display_name,
                avatar_url=message.author.avatar_url,
            )
        except:
            return False
        else:
            return True

    
    # Bot Commands

    @commands.group()
    @checks.guildowner_or_permissions()
    async def setsoju(self, ctx: commands.Context):
        """Set Soju Player settings"""
        if not ctx.invoked_subcommand:
            # Global settings
            e = discord.Embed(color=(await ctx.embed_colour()), title="Guild Settings", description="")
            e.add_field(name="sojuEnabled", value=(await self.config.guild(ctx.guild).sojuEnabled()), inline=False)
            e.add_field(name="sojuInstance", value=(await self.config.guild(ctx.guild).sojuInstance()), inline=False)
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

    @commands.command()
    async def playsoju(self, ctx, spotifyLink, asMyself: bool=False):
        """Return a Soju link
        
        Can set asMyself to true/false, for sending as webhook"""
        sojuInstance = await self.config.guild(ctx.guild).sojuInstance()
        sendMsg = "https://{sojuInstance}?s={spotifyLink}\n".format(sojuInstance, spotifyLink)

        if asMyself == False:
            return await ctx.send(sendMsg)
        elif asMyself == True:
            webhookUrl = await self.webhookFinder(ctx, self.bot)
            if webhookUrl == False:
                return await ctx.send(sendMsg)
            webhookSender = await self.webhookSender(ctx, webhookUrl, sendMsg)
            if webhookSender is not True:
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
        sojuEnabled = await self.config.guild(message.guild).sojuEnabled()
        if sojuEnabled is not True:
            return
        regexString = r"https\:\/\/open\.spotify\.com\/\w{4,12}\/\w{14,26}(?=\?|$)"
        matches = re.finditer(regexString, message.clean_content)
        if len(matches) <= 0:
            return

        sojuInstance = await self.config.guild(message.guild).sojuInstance()
        sendMsg = ""

        for matchNum, match in enumerate(matches, start=1):
            print(matchNum)
            sendMsg += "https://{sojuInstance}?s={match}\n".format(sojuInstance = sojuInstance, match = match.group())
        
        webhookUrl = await self.webhookFinder(message, self.bot)
        if webhookUrl == False:
            return await message.channel.send(sendMsg)
        webhookSender = await self.webhookSender(message, webhookUrl, sendMsg)
        if webhookSender is not True:
            return await message.channel.send(sendMsg)
        else:
            try:
                message.delete()
            except:
                pass
