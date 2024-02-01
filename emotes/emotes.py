from redbot.core import Config, app_commands, commands, checks
from typing import Union
import asyncio
import aiohttp
import discord
from discord import Webhook, SyncWebhook
import requests
import time
import random
import re
from collections import OrderedDict

import logging
logger = logging.getLogger(__name__)

from .cherry import Cherry
from .esheet import EmoteSheet

class Emotes(commands.Cog):
    """Custom emote solution for non-nitro users"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=806715409318936616)

        # select for :emotetext: but not <a:emotetext:123456789>
        self.RegexEmoteText = r"(?<=^|(?<=[^<a]))(:\w{2,32}:)"
        # select for the full <(a):emotetext:123456789>
        self.RegexFullEmoteSearch = r"(<a?:\w{2,32}:\d{14,22}>)"
        # parse emotetext from <a:emotetext:123456789>
        self.RegexGetEmoteText = r"(?<=:)\w{2,32}(?=:)"
        # parse 123456789 from <a:emotetext:123456789>
        self.RegexGetEmoteId = r"(?<=:)\d{14,22}(?=>)"

        # Bot owner configs
        default_global = {
            "emoteGoogleSheetId": "",
            "emoteStore": [],
            "cherryAll": True,
            "cherryEmoteSheet": False,
            "cherryRecents": True,
            "cherryRecentsMax": 20,
            "cherryServer": True,
        }
        self.config.register_global(**default_global)

        # Server owner configs
        default_guild = {
            "cherryGuildAll": True,
            # "cherryGuildEmoteSheet": True,
            # "cherryGuildRecents": True,
            "cherryGuildRecentsMax": 10,
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

    @commands.hybrid_group(name="setemotes", aliases=["se", "setemote", "setemotesheet"])
    async def setemotes(self, ctx: commands.Context):
        """Change the configurations for Emotes Cog
        
        Setting global values to `False` will override guild settings and disable it across the whole bot."""
        if not ctx.invoked_subcommand:
            pass

    @setemotes.command(name="settings", aliases=["info"])
    @checks.is_owner()
    async def seteosettings(self, ctx):
        """Display current config"""
        # Global settings
        eo = discord.Embed(color=(await ctx.embed_colour()), title="Bot Owner", description="*[ Global settings ]*")
        eo.add_field(name="All", value=(await self.config.cherryAll()), inline=False)
        eo.add_field(name="Emote Sheet", value=(await self.config.cherryEmoteSheet()))
        eo.add_field(name="Recents", value=(await self.config.cherryRecents()))
        eo.add_field(name="Recents max", value=(await self.config.cherryRecentsMax()))
        eo.add_field(name="Server Emotes", value=(await self.config.cherryServer()))
        await ctx.send(embed=eo)
        # Server settings
        eg = discord.Embed(color=(await ctx.embed_colour()), title="Server", description="*[ Guild settings ]*")
        eg.add_field(name="All", value=(await self.config.guild(ctx.guild).cherryGuildAll()), inline=False)
        eg.add_field(name="Recents max", value=(await self.config.guild(ctx.guild).cherryGuildRecentsMax()))
        await ctx.send(embed=eg)

    @setemotes.command(name="all")
    @checks.is_owner()
    async def seteoall(self, ctx, true_or_false: bool):
        """The power switch for all of Cherry Emotes"""
        await self.config.cherryAll.set(true_or_false)
        await ctx.message.add_reaction("✅")

    @setemotes.command(name="guildall")
    @checks.guildowner_or_permissions(administrator=True)
    async def seteall(self, ctx, true_or_false: bool):
        """The power switch for Cherry Emotes in this server"""
        await self.config.guild(ctx.guild).cherryGuildAll.set(true_or_false)
        await ctx.message.add_reaction("✅")

    @setemotes.command(name="recents")
    @checks.is_owner()
    async def seteorecents(self, ctx, true_or_false: bool):
        """Enable the use of searching recent messages for emotes"""
        await self.config.cherryRecents.set(true_or_false)
        await ctx.message.add_reaction("✅")

    @setemotes.command(name="recentsmax")
    @checks.is_owner()
    async def seteorecentscount(self, ctx, count: int):
        """Determines how many messages back to search for emotes
        
        Not recommended to set higher than 20, for performance reasons."""
        await self.config.cherryRecentsMax.set(count)
        await ctx.message.add_reaction("✅")

    @setemotes.command(name="guildrecentsmax")
    @checks.guildowner_or_permissions(administrator=True)
    async def seterecentscount(self, ctx, count: int):
        """Determines how many messages back to search for emotes in this server
        
        Not recommended to set higher than 20, for performance reasons."""
        # Make sure guild setting doesn't exceed bot owner setting
        botMax = await self.config.cherryRecentsMax()
        if botMax >= count:
            await self.config.guild(ctx.guild).cherryGuildRecentsCount.set(count)
            return await ctx.message.add_reaction("✅")
        else:
            return await ctx.send(f"Error: Please set a number lower than {botMax}.") 
        
    @setemotes.command(name="server", aliases=["animated"])
    @checks.is_owner()
    async def seteoserver(self, ctx, true_or_false: bool):
        """Enable the use of server animated emotes"""
        await self.config.cherryServer.set(true_or_false)
        await ctx.message.add_reaction("✅")

    @setemotes.group(name="sheet")
    @checks.is_owner()
    async def seteosheet(self, ctx: commands.Context):
        """Set up Emote Sheets

        Allows users to pull from a Google Sheet of saved emotes.

        For more information, see https://coffeebank.github.io/coffee-cogs/emotes
        
        To set Google Sheets API key, use the command **`[p]set api gsheets api_key,YOURKEYHERE`**"""
        if not ctx.invoked_subcommand:
            pass
    
    @seteosheet.command(name="settings", aliases=["info"])
    async def setesinfo(self, ctx):
        """Display current config"""
        # Global settings
        eo = discord.Embed(color=(await ctx.embed_colour()), title="Bot Owner", description="*[ Global settings ]*")
        eo.add_field(name="Emote Sheet ID", value=(await self.config.emoteGoogleSheetId()), inline=False)
        eo.add_field(name="Emote Sheet Enabled", value=(await self.config.cherryEmoteSheet()), inline=False)
        await ctx.send(embed=eo)
    
    @seteosheet.command(name="id")
    async def setessheet(self, ctx, sheet_id: str):
        """Set Emote Google Sheet's ID, where the emote data was entered into"""
        await self.config.emoteGoogleSheetId.set(sheet_id)
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
        # ignore if no intents
        if not message.content or message.content == "":
            return
        cherryAll = await self.config.cherryAll()
        if cherryAll is not True:
            return
        cherryGuildAll = await self.config.guild(message.guild).cherryGuildAll()
        if cherryGuildAll is not True:
            return
        # search is faster than match, but either work: https://stackoverflow.com/a/49710946/15923512
        if re.search(self.RegexEmoteText, message.clean_content) == None:
            return

        # Message object
        sendMsg = message.clean_content
        sendMsgArray = []
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
                # # if emoteNames in emoteStore:
                # # regex parse emoteId from url
                # # if png: if gif:
                # # replace emoteNames with <(a):emotename:emoteId>
                # sendMsg = Cherry.esheetProcessor(self, sendMsg, emoteNames, emoteStore)

                # Oct 2023 Update: Support for emotes is deprecated due to Discord limitations
                # if emoteNames in emoteStore:
                # send image url as size of emote (64px, since 48px doesn't work on /emoji/ urls)
                emoteLinksArray = Cherry.esheetProcessorLinks(self, sendMsg, emoteNames, emoteStore)
                sendMsgArray += emoteLinksArray

        # If nothing changed between sendMsg assignment and now, it means no emotes, return
        if sendMsg == message.clean_content and sendMsgArray == []:
            return
        
        # Build webhook to send
        webhookUrl = await Cherry.webhookFinder(self, message, self.bot)
        if webhookUrl == False:
            return await message.channel.send("Help! I'm missing webhook permissions!")
        webhookSender = await Cherry.webhookSender(self, message, webhookUrl, sendMsg)
        if webhookSender is not True:
            return await message.channel.send("An unknown error occured when trying to send to webhook.")
        for sm in sendMsgArray:
            await Cherry.webhookSender(self, message, webhookUrl, sm)

        # Now that the sending was successful, we can delete the message
        # Silently fail if message delete fails, since we've already succeeded webhook
        try:
            await message.delete()
        except:
            pass


    ## EmoteSheet:
    ## EmoteSheet is the engine behind integrating with the Google Sheets API to create a searchable emote database inside the bot.

    @commands.hybrid_command(aliases=["esearch", "ee"])
    @app_commands.describe(search="Search for image-ized emote url")
    async def emotesearch(self, ctx, search, page: int=1):
        """Search for image-ized emote url"""
        emoteStore = await self.config.emoteStore()
        await EmoteSheet.search(self, ctx, emoteStore, search, page)

    @commands.hybrid_command(aliases=["esend", "eee"])
    @app_commands.describe(search="Send an emote from Emote Sheet, with first search result")
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

        # Now that the sending was successful, we can delete the message
        # Silently fail if message delete fails, since we've already succeeded webhook
        try:
            await ctx.message.delete()
        except:
            pass


    @commands.hybrid_command(aliases=["ei"])
    @app_commands.describe(emote="Send info about an emote")
    async def emoteinfo(self, ctx, emote=None):
        """Send info about an emote

        If you don't have access to the emote (ie. no Nitro, or can't send the emote because it's from another server), you can reply to the message with the emote you want and the `[p]emoteinfo` command will pick up the emote."""

        # discord/app_commands/transformers.py:819 in get_supported_annotation
        # TypeError: unsupported types given inside typing.Union[discord.emoji.Emoji, discord.partial_emoji.PartialEmoji]
        if emote is not None and isinstance(emote, (discord.Emoji, discord.PartialEmoji)) is not True:
            return

        if emote:
            ttl = str(emote.id)
            desc = str(emote.url)
            e = discord.Embed(color=(await ctx.embed_colour()), title=ttl, description=desc)
            e.set_thumbnail(url=emote.url)
            return await ctx.send(embed=e)
        else:
            if ctx.message.reference and (ctx.message.type == discord.MessageType.default or ctx.message.type == discord.MessageType.reply):
                # Build emote bank out of referenced message (reply)
                recentsBankBuilder = Cherry.recentsBankBuilder(self, [ctx.message.reference.resolved], self.RegexFullEmoteSearch)
                # Only run if there's more emotes inside recentsBankBuilder
                if recentsBankBuilder is not False:
                    for ee in recentsBankBuilder:
                        eeText = re.findall(self.RegexGetEmoteText, ee)
                        eeId = re.findall(self.RegexGetEmoteId, ee)
                        if "a:" in ee:
                            desc = "https://cdn.discordapp.com/emojis/"+str(eeId[0])+".gif"
                        else:
                            desc = "https://cdn.discordapp.com/emojis/"+str(eeId[0])+".png"
                        eeSend = discord.Embed(color=(await ctx.embed_colour()), title=str(eeText[0]), description=str(desc))
                        eeSend.set_thumbnail(url=desc)
                        await ctx.send(embed=eeSend)
                    return await ctx.message.add_reaction("✅")
                else:
                    return await ctx.message.add_reaction("💨")
            else:
                return await ctx.message.add_reaction("💨")

    @commands.hybrid_command()
    @app_commands.describe(hist="List all emotes in a replied-to message, in a code block")
    async def emotelist(self, ctx, hist=False):
        """List all emotes in message

        Shows a list of names and urls for all emotes in a message, when you reply to a message with this command. Useful for Emote Spreadsheet.
        """
        if hist is True:
          messageCountRaw = await ctx.channel.history(limit=None, after=ctx.message.reference.resolved).flatten()
          messageCount = len(messageCountRaw)
          messages = await ctx.channel.history(limit=messageCount).flatten()
        else:
          messages = [ctx.message.reference.resolved]

        for msg in messages:
          if msg.type == discord.MessageType.default:
            msgObj = msg
          else:
            pass # return await ctx.message.add_reaction("💨")

          # Build emote bank out of previous chat history
          recentsBankBuilder = Cherry.recentsBankBuilder(self, [msg], self.RegexFullEmoteSearch)
          # Only run if there's more emotes inside recentsBankBuilder
          if recentsBankBuilder is not False:
              finalList = ""
              for ee in recentsBankBuilder:
                  eeText = re.findall(self.RegexGetEmoteText, ee)
                  eeId = re.findall(self.RegexGetEmoteId, ee)
                  if "a:" in ee:
                      desc = "https://cdn.discordapp.com/emojis/"+str(eeId[0])+".gif?v=1"
                  else:
                      desc = "https://cdn.discordapp.com/emojis/"+str(eeId[0])+".png?v=1"
                  finalList += str(eeText[0]).lower()+","+str(desc)+"\n"
              await ctx.send("```\n"+str(finalList)+"```")
              await ctx.message.add_reaction("✅")
          else:
              await ctx.message.add_reaction("💨")

    @commands.hybrid_command()
    @app_commands.describe(emoteurl="Show an emote you have an URL for")
    async def showemote(self, ctx, emoteurl: str):
        """Show an emote you have an URL for"""
        emoteName = "showemote"
        if isinstance(emoteUrl, str):
            try:
                emoteId = re.findall(r"(?<=emojis/)(\d{16,20})(?=\.)", emoteUrl)[0]
            except:
                return await ctx.send("Invalid emote")

        sendMsg = Cherry.emoteBuilder(self, emoteName=emoteName, emoteId=emoteId, emoteAnimated=Cherry.emoteAnimated(self, emoteUrl))

        # Build webhook to send
        webhookUrl = await Cherry.webhookFinder(self, ctx, self.bot)
        if webhookUrl == False:
            return await ctx.send("Help! I'm missing webhook permissions!")
        webhookSender = await Cherry.webhookSender(self, ctx, webhookUrl, sendMsg)
        if webhookSender is not True:
            return await ctx.send("An unknown error occured when trying to send to webhook.")
