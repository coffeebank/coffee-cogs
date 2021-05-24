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

        default_global = {
            "emoteGoogleSheetId": "",
            "emoteStore": [],
            "cherryAll": True,
            "cherryRecents": False,
            "cherryRecentsCount": 6,
            "cherryServer": True,
        }
        self.config.register_global(**default_global)

    # This cog does not store any End User Data
    async def red_get_data_for_user(self, *, user_id: int):
        return {}
    async def red_delete_data_for_user(self, *, requester, user_id: int) -> None:
        pass



    ## Cherry Emotes:
    ## Cherry Emotes is the engine behind interacting with emotes in chat for non-nitro users using webhooks.
    
    @commands.group()
    @checks.is_owner()
    async def setemote(self, ctx: commands.Context):
        """Change the configurations for Cherry Emotes. Allows users to use nitro-like features.
        
        Only the bot owner has access to these commands, and these settings are global across all servers the bot is in.
        
        `all` overrides all other settings to disable everything, for performance reasons. Setting `all` to True allows you to customize which features you want on/off.
        """
        if not ctx.invoked_subcommand:
            all = await self.config.cherryAll()
            recents = await self.config.cherryRecents()
            recentsCount = await self.config.cherryRecentsCount()
            server = await self.config.cherryServer()
            await ctx.send("```"
                f"all: {all}\n"
                f"recents: {recents}\n"
                f"recentsCount: {recentsCount}\n"
                f"server: {server}\n"
            "```")

    @setemote.command(name="all")
    async def seteall(self, ctx, TrueOrFalse: bool):
        """The power switch for all of Cherry Emotes"""
        await self.config.cherryAll.set(TrueOrFalse)
        await ctx.message.add_reaction("✅")
        
    @setemote.command(name="server", aliases=["animated"])
    async def seteserver(self, ctx, TrueOrFalse: bool):
        """Enable the use of this server's animated emotes"""
        await self.config.cherryServer.set(TrueOrFalse)
        await ctx.message.add_reaction("✅")

    @setemote.command(name="recents")
    async def seterecents(self, ctx, TrueOrFalse: bool):
        """Enable the use of searching recent messages for emotes"""
        await self.config.cherryRecents.set(TrueOrFalse)
        await ctx.message.add_reaction("✅")

    @setemote.command(name="recentscount")
    async def seterecentscount(self, ctx, count: int):
        """Determines how many messages back to search for emotes
        
        Not recommended to set higher than 6, for performance reasons."""
        await self.config.cherryRecentsCount.set(count)
        await ctx.message.add_reaction("✅")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if message.webhook_id:
            return
        if message.guild is None:
            return
        cherryAll = await self.config.cherryAll()
        if cherryAll == False:
            return

        # Message object
        sendMsg = message.clean_content
        emoteNames = None

        # cherryServer
        cherryServer = await self.config.cherryServer()
        if cherryServer == True:
            # Get list of :emote: items
            emoteNames = await Cherry.cherryEmoteParser(self, self.RegexEmoteText, sendMsg)
            if emoteNames is not False:
                # Retrieve guild emotes, if emoteName matches, it adds emoteObj to emoteBank
                emoteBank = await Cherry.cherryEmoteBank(self, message, emoteNames)
                # Loops through emoteBank if it's not empty
                if emoteBank is not False:
                    for item in emoteBank:
                        sendMsg = re.sub(fr"(^|(?<=[^<a])):{item.name}:", Cherry.cherryEmoteBuilder(self, item, buildNormal=False), sendMsg)

        # cherryRecents
        cherryRecents = await self.config.cherryRecents()
        if cherryRecents == True:
            # Get new list of :emote: items, after cherryServer has replaced :emotes:
            # Only run if there's still :emote: items left
            emoteNames = await Cherry.cherryEmoteParser(self, self.RegexEmoteText, sendMsg)
            if emoteNames is not False:
                # Get previous chat history
                cherryRecentsCount = await self.config.cherryRecentsCount()
                cherryChatHistory = await Cherry.cherryGetChatHistory(self, message, cherryRecentsCount)
                if cherryChatHistory == False:
                    return await message.channel.send("Oops, I'm missing Message History permissions....")
                # Build emote bank out of previous chat history
                cherryHistEmoteBank = Cherry.cherryHistEmoteBank(self, cherryChatHistory, self.RegexFullEmoteSearch)
                # Only run if there's more emotes inside cherryHistEmoteBank
                if cherryHistEmoteBank is not False:
                    sendMsg = Cherry.cherryHistInsertEmotes(self, sendMsg, cherryHistEmoteBank, emoteNames)

        # If nothing changed between sendMsg assignment and now, it means no emotes, return
        if sendMsg == message.clean_content:
            return
        
        # Build webhook to send
        webhookUrl = await Cherry.cherryWebhookFinder(self, message, self.bot)
        if webhookUrl is not False:
            async with aiohttp.ClientSession() as session:
                webhook = Webhook.from_url(webhookUrl, adapter=AsyncWebhookAdapter(session))
                try:
                    await webhook.send(
                        sendMsg,
                        username=message.author.display_name,
                        avatar_url=message.author.avatar_url,
                    )
                except:
                    await message.channel.send("An unknown error occured when trying to send to webhook.")
                else:
                    # Now that the sending was successful, we can delete the message
                    # Silently fail if message delete fails
                    try:
                        await message.delete()
                    except:
                        pass
        else:
            await message.channel.send("Help! I'm missing webhook permissions!")



    ## EmoteSheet:
    ## EmoteSheet is the engine behind integrating with the Google Sheets API to create a searchable emote database inside the bot.

    @commands.group(aliases=["se"])
    @checks.is_owner()
    async def setemotesheet(self, ctx: commands.Context):
        """Change the configurations for Emotes Spreadsheet

        For more information, see https://github.com/coffeebank/coffee-cogs/wiki
        
        To set Google Sheets API key, use the command **`[p]set api gsheets api_key,YOURKEYHERE`**"""
        if not ctx.invoked_subcommand:
            pass
    
    @setemotesheet.command(name="sheet")
    async def setessheet(self, ctx, sheetId: str):
        """Set Emote Google Sheet's ID, where the emote data was entered into"""
        await self.config.emoteGoogleSheetId.set(sheetId)
        await ctx.message.add_reaction("✅")

    @setemotesheet.command(name="update")
    async def setesupdate(self, ctx):
        """Pull updates from Emote Google Sheet"""
        await ctx.message.add_reaction("⏳")
        gsheets_data = await self.config.emoteGoogleSheetId()
        emotearray = await EmoteSheet.emoteSheetUpdate(self, ctx, self.bot, gsheets_data)
        # Commit the changes
        await self.config.emoteStore.set(emotearray)
        await ctx.message.add_reaction("✅")

    @commands.command(aliases=["esearch", "ee"])
    async def emotesearch(self, ctx, search, page: int=1):
        """Search for image-ized emote url"""
        emoteStore = await self.config.emoteStore()
        await EmoteSheet.emoteSheetSearch(self, ctx, emoteStore, search, page)

    @commands.command(aliases=["esend", "eee"])
    async def emotesend(self, ctx, search):
        """Send an image-ized emote url, with first search result"""
        emoteStore = await self.config.emoteStore()
        await EmoteSheet.emoteSheetSend(self, ctx, search, emoteStore)

    @commands.command(aliases=["ei"])
    async def emoteinfo(self, ctx, emote: Union[discord.Emoji, discord.PartialEmoji]):
        """Send info about an emote"""
        ttl = str(emote.id)
        desc = str(emote.url)
        e = discord.Embed(color=(await ctx.embed_colour()), title=ttl, description=desc)
        e.set_thumbnail(url=emote.url)
        await ctx.send(embed=e)
        
