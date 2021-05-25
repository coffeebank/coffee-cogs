# from redbot.core import Config
from redbot.core import Config, commands, checks
from typing import Union
import asyncio
import aiohttp
import discord
from discord import Webhook, AsyncWebhookAdapter
import requests
import time
import random
import re
from collections import OrderedDict

from .cherry import Cherry
from .esheet import EmoteSheet

class Emotes(commands.Cog):
    """Custom emote solution for non-nitro users"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=806715409318936616)

        # :emotetext: but not <a:emotetext:123456789> 
        self.RegexEmoteText = r"(?<=^|(?<=[^<a]))(:\w{2,16}:)"
        # the full <(a):emotetext:123456789>
        self.RegexFullEmoteSearch = r"(<a?:\w{2,16}:\d{14,20}>)"

        # Bot owner configs
        default_global = {
            "emoteGoogleSheetId": "",
            "emoteStore": [],
            "cherryAll": True,
            "cherryEmoteSheet": False,
            "cherryRecents": True,
            "cherryRecentsMax": 6,
            "cherryServer": True,
        }
        self.config.register_global(**default_global)
        # Server owner configs
        default_guild = {
            "cherryGuildAll": True,
            # "cherryGuildEmoteSheet": True,
            # "cherryGuildRecents": True,
            # "cherryGuildServer": True,
        }
        self.config.register_guild(**default_guild)

    # This cog does not store any End User Data
    async def red_get_data_for_user(self, *, user_id: int):
        return {}
    async def red_delete_data_for_user(self, *, requester, user_id: int) -> None:
        pass



    ## Set Emote Settings:
    ## Falsy values override all server-level settings

    @commands.group(aliases=["se", "setemote", "setemotesheet"])
    async def setemotes(self, ctx: commands.Context):
        """Change the configurations for Emotes Cog
        
        Setting global values to `False` will override guild settings and disable it across the whole bot."""
        if not ctx.invoked_subcommand:
            # Global settings
            eo = discord.Embed(color=(await ctx.embed_colour()), title="Bot Owner", description="*[ Global settings ]*")
            eo.add_field(name="All", value=(await self.config.cherryAll()), inline=False)
            eo.add_field(name="Emote Sheet", value=(await self.config.cherryEmoteSheet()))
            eo.add_field(name="Recents", value=(await self.config.cherryRecents()))
            eo.add_field(name="Recents max", value=(await self.config.cherryRecentsMax()))
            eo.add_field(name="Server", value=(await self.config.cherryServer()))
            await ctx.send(embed=eo)
            # Server settings
            eg = discord.Embed(color=(await ctx.embed_colour()), title="Server", description="*[ Guild settings ]*")
            eg.add_field(name="All", value=(await self.config.cherryGuildAll()), inline=False)
            await ctx.send(embed=eg)

    @setemotes.command(name="all")
    @checks.is_owner()
    async def seteoall(self, ctx, TrueOrFalse: bool):
        """The power switch for all of Cherry Emotes"""
        await self.config.cherryAll.set(TrueOrFalse)
        await ctx.message.add_reaction("✅")

    @setemotes.command(name="guildall")
    @checks.guildowner_or_permissions()
    async def seteall(self, ctx, TrueOrFalse: bool):
        """The power switch for Cherry Emotes in this server"""
        await self.config.cherryGuildAll.set(TrueOrFalse)
        await ctx.message.add_reaction("✅")

    @setemotes.command(name="recents")
    @checks.is_owner()
    async def seteorecents(self, ctx, TrueOrFalse: bool):
        """Enable the use of searching recent messages for emotes"""
        await self.config.cherryRecents.set(TrueOrFalse)
        await ctx.message.add_reaction("✅")

    @setemotes.command(name="recentsmax")
    @checks.is_owner()
    async def seteorecentscount(self, ctx, count: int):
        """Determines how many messages back to search for emotes
        
        Not recommended to set higher than 6, for performance reasons."""
        await self.config.cherryRecentsMax.set(count)
        # Make sure guild setting doesn't exceed bot owner setting
        # guildVal = await self.config.cherryRecentsMax()
        # if guildVal > count:
        #     await self.config.cherryGuildRecentsCount.set(count)
        await ctx.message.add_reaction("✅")
        
    @setemotes.command(name="server", aliases=["animated"])
    @checks.is_owner()
    async def seteoserver(self, ctx, TrueOrFalse: bool):
        """Enable the use of server animated emotes"""
        await self.config.cherryServer.set(TrueOrFalse)
        await ctx.message.add_reaction("✅")

    @setemotes.group(name="sheet")
    @checks.is_owner()
    async def seteosheet(self, ctx: commands.Context):
        """Set up Emote Sheets

        Allows users to pull from a Google Sheet of saved emotes.

        For more information, see https://github.com/coffeebank/coffee-cogs/wiki/Emotes
        
        To set Google Sheets API key, use the command **`[p]set api gsheets api_key,YOURKEYHERE`**"""
        if not ctx.invoked_subcommand:
            # Global settings
            eo = discord.Embed(color=(await ctx.embed_colour()), title="Bot Owner", description="*[ Global settings ]*")
            eo.add_field(name="Emote Sheet ID", value=(await self.config.emoteGoogleSheetId()), inline=False)
            eo.add_field(name="Emote Sheet Enabled", value=(await self.config.cherryEmoteSheet()), inline=False)
            await ctx.send(embed=eo)
    
    @seteosheet.command(name="id")
    async def setessheet(self, ctx, sheetId: str):
        """Set Emote Google Sheet's ID, where the emote data was entered into"""
        await self.config.emoteGoogleSheetId.set(sheetId)
        await self.config.cherryEmoteSheet.set(True)
        await ctx.message.add_reaction("✅")
        
    @seteosheet.command(name="true")
    async def setestrue(self, ctx):
        """Enable the use of Emote Sheets by the bot
        
        Will automatically set to True when you set an Emote Sheet"""
        emoteGoogleSheetId = await self.config.emoteGoogleSheetId()
        if emoteGoogleSheetId == "":
            return await ctx.send("Emote Sheet isn't set up yet. Try setting it up first!")
        else:
            await self.config.cherryEmoteSheet.set(True)
            await ctx.message.add_reaction("✅")
        
    @seteosheet.command(name="false")
    async def setesfalse(self, ctx):
        """Disable the use of Emote Sheets by the bot"""
        await self.config.cherryEmoteSheet.set(False)
        await ctx.message.add_reaction("✅")

    @seteosheet.command(name="update")
    async def setesupdate(self, ctx):
        """Pull updates from Emote Google Sheet"""
        await ctx.message.add_reaction("⏳")
        gsheets_data = await self.config.emoteGoogleSheetId()
        emotearray = await EmoteSheet.update(self, ctx, self.bot, gsheets_data)
        # Crude error handling, might refactor someday....
        if isinstance(emotearray, str):
            await ctx.message.add_reaction("❎")
            return await ctx.send(emotearray)
        # Commit the changes
        await self.config.emoteStore.set(emotearray)
        await ctx.message.add_reaction("✅")



    ## Cherry Emotes:
    ## Cherry Emotes is the engine behind interacting with emotes in chat for non-nitro users using webhooks.

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if message.webhook_id:
            return
        if message.guild is None:
            return
        cherryAll = await self.config.cherryAll()
        if cherryAll is not True:
            return
        cherryGuildAll = await self.config.cherryGuildAll()
        if cherryGuildAll is not True:
            return
        # search is faster than match, but either work: https://stackoverflow.com/a/49710946/15923512
        if re.search(self.RegexEmoteText, message.clean_content) == None:
            return

        # Message object
        sendMsg = message.clean_content
        emoteNames = None

        # cherryServer
        cherryServer = await self.config.cherryServer()
        if cherryServer == True:
            # Get list of :emote: items
            emoteNames = await Cherry.emoteParser(self, self.RegexEmoteText, sendMsg)
            if emoteNames is not False:
                # Retrieve guild emotes, if emoteName matches, it adds emoteObj to emoteBank
                emoteBank = await Cherry.serverBankBuilder(self, message, emoteNames)
                # Loops through emoteBank if it's not empty
                if emoteBank is not False:
                    for item in emoteBank:
                        sendMsg = re.sub(fr"(^|(?<=[^<a])):{item.name}:", Cherry.emoteBuilder(self, emote=item, buildNormal=False), sendMsg)

        # cherryRecents
        cherryRecents = await self.config.cherryRecents()
        if cherryRecents == True:
            # Get new list of :emote: items, after cherryServer has replaced :emotes:
            # Only run if there's still :emote: items left
            emoteNames = await Cherry.emoteParser(self, self.RegexEmoteText, sendMsg)
            if emoteNames is not False:
                # Get previous chat history
                cherryRecentsMax = await self.config.cherryRecentsMax()
                cherryChatHistory = await Cherry.recentsHistRetriever(self, message, cherryRecentsMax)
                if cherryChatHistory == False:
                    return await message.channel.send("Oops, I'm missing Message History permissions....")
                # Build emote bank out of previous chat history
                recentsBankBuilder = Cherry.recentsBankBuilder(self, cherryChatHistory, self.RegexFullEmoteSearch)
                # Only run if there's more emotes inside recentsBankBuilder
                if recentsBankBuilder is not False:
                    # Modifies sendMsg using given data
                    sendMsg = Cherry.recentsProcessor(self, sendMsg, recentsBankBuilder, emoteNames)

        # cherryEmoteSheet
        cherryEmoteSheet = await self.config.cherryEmoteSheet()
        if cherryEmoteSheet == True:
            # Get new list of :emote: items, after cherryServer has replaced :emotes:
            # Only run if there's still :emote: items left
            emoteNames = await Cherry.emoteParser(self, self.RegexEmoteText, sendMsg)
            if emoteNames is not False:
                emoteStore = await self.config.emoteStore()
                # if emoteNames in emoteStore:
                # regex parse emoteId from url
                # if png: if gif:
                # replace emoteNames with <(a):emotename:emoteId>
                sendMsg = Cherry.esheetProcessor(self, sendMsg, emoteNames, emoteStore)

        # If nothing changed between sendMsg assignment and now, it means no emotes, return
        if sendMsg == message.clean_content:
            return
        
        # Build webhook to send
        webhookUrl = await Cherry.webhookFinder(self, message, self.bot)
        if webhookUrl == False:
            return await message.channel.send("Help! I'm missing webhook permissions!")
        webhookSender = await Cherry.webhookSender(self, message, webhookUrl, sendMsg)
        if webhookSender is not True:
            return await message.channel.send("An unknown error occured when trying to send to webhook.")


    ## EmoteSheet:
    ## EmoteSheet is the engine behind integrating with the Google Sheets API to create a searchable emote database inside the bot.

    @commands.command(aliases=["esearch", "ee"])
    async def emotesearch(self, ctx, search, page: int=1):
        """Search for image-ized emote url"""
        emoteStore = await self.config.emoteStore()
        await EmoteSheet.search(self, ctx, emoteStore, search, page)

    @commands.command(aliases=["esend", "eee"])
    async def emotesend(self, ctx, search):
        """Send an emote from Emote Sheet, with first search result"""
        emoteStore = await self.config.emoteStore()
        searchObj = EmoteSheet.searchsingle(self, search, emoteStore)
        if searchObj == False:
            return await ctx.message.add_reaction("💨")
        # [1] is emote name
        emoteName = searchObj[1]
        # [2] is emote url
        emoteId = re.findall(r"(?<=emojis/)(\d{16,20})(?=\.)", searchObj[2])[0]
        # Build emote object
        sendMsg = Cherry.emoteBuilder(self,
          emoteName=emoteName,
          emoteId=emoteId,
          emoteAnimated=Cherry.emoteAnimated(self, searchObj[2])
        )
        # Build webhook to send
        webhookUrl = await Cherry.webhookFinder(self, ctx, self.bot)
        if webhookUrl == False:
            return await ctx.send("Help! I'm missing webhook permissions!")
        webhookSender = await Cherry.webhookSender(self, ctx, webhookUrl, sendMsg)
        if webhookSender is not True:
            return await ctx.send("An unknown error occured when trying to send to webhook.")

    @commands.command(aliases=["ei"])
    async def emoteinfo(self, ctx, emote: Union[discord.Emoji, discord.PartialEmoji]):
        """Send info about an emote"""
        ttl = str(emote.id)
        desc = str(emote.url)
        e = discord.Embed(color=(await ctx.embed_colour()), title=ttl, description=desc)
        e.set_thumbnail(url=emote.url)
        await ctx.send(embed=e)
