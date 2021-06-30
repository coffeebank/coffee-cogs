from redbot.core import Config, commands, checks
from redbot.core.utils.predicates import ReactionPredicate
from redbot.core.utils.menus import start_adding_reactions
from urllib.request import urlopen
import mimetypes
import discord
from discord import Webhook, AsyncWebhookAdapter
import aiohttp
import asyncio
import random
import requests
import json
import base64
from io import BytesIO

class Msgmover(commands.Cog):
    """Move messages around, cross-channels, cross-server!
    
    msgrelay: Forward all of a channel's messages to another channel/server
    msgcopy: Copy a set # of past messages to another channel/server"""

    def __init__(self, bot):
        self.config = Config.get_conf(self, identifier=806715409318936616)
        self.bot = bot
        default_global = {
            "msgrelayChannels": [],
            "msgrelayStore": {}
        }
        self.config.register_global(**default_global)

        # Add server-level configs
        default_guild = {
            "msgrelayStoreV2": {},
            # {
            #     'chanId': {
            #         'option': bool,
            #         'toChanId': str,
            #         'toWebhook': str,
            #         'attachsAsUrl': bool,
            #     },
            # }
        }
        self.config.register_guild(**default_guild)

    # This cog does not store any End User Data
    async def red_get_data_for_user(self, *, user_id: int):
        return {}
    async def red_delete_data_for_user(self, *, requester, user_id: int) -> None:
        pass


    # Utility Commands

    async def msgFormatter(self, webhook, message, attachsAsUrl=False, userProfiles=True):
        # webhook: A webhook object from discord.py
        # message: A message object from discord.py
        # attachsAsUrl: Sets whether attachments should be linked using URLS, or re-uploaded as an independent file
        # userProfiles: Sets whether messages use the sender's user avatars

        msgContent = message.clean_content

        # Add reply if it exists
        if message.reference:
            # Retrieve replied-to message
            refObj = message.reference.resolved
            replyEmbed = discord.Embed(color=discord.Color(value=0x25c059), description="")
            # Check whether message is empty
            if refObj.clean_content:
                replyBody = (refObj.clean_content[:56] + '...') if len(refObj.clean_content) > 56 else refObj.clean_content
            else:
                replyBody = "Click to see attachment 🖼️"
            # Create link to message
            replyTitle = f"↪️ {replyBody}"
            replyEmbed.set_author(name=replyTitle, icon_url=refObj.author.avatar_url, url=refObj.jump_url)
            # Send this before the original message so that the embed appears above the message in chat
            await webhook.send(
                username=message.author.display_name,
                avatar_url=message.author.avatar_url,
                embed=replyEmbed
            )

        # Add embed if exists
        # Do not set the embed if it came from a http link in the message (fixes repo issue #4)
        if message.embeds and "http" not in msgContent:
            msgEmbed = message.embeds
        else:
            msgEmbed = None

        # Add attachment if exists
        if message.attachments and attachsAsUrl == True:
            for msgAttach in message.attachments:
                msgContent = msgContent+str(msgAttach.url)+"\n"

        # Settings
        if userProfiles == True:
            userProfilesName = message.author.display_name
            userProfilesAvatar = message.author.avatar_url
        else:
            userProfilesName = None
            userProfilesAvatar = None

        # Send core message
        try:
            await webhook.send(
                msgContent,
                username=userProfilesName,
                avatar_url=userProfilesAvatar,
                embeds=msgEmbed
            )
        except:
            pass
        
        # Send full attachments
        if message.attachments and attachsAsUrl == False:
            for msgAttach in message.attachments:
                try:
                    await webhook.send(
                        username=message.author.display_name,
                        avatar_url=message.author.avatar_url,
                        file=await msgAttach.to_file()
                    )
                except:
                    # Couldn't send, retry sending file as url only
                    await webhook.send(
                        "File: "+str(msgAttach.url), 
                        username=message.author.display_name,
                        avatar_url=message.author.avatar_url
                    )

        # Need to tell endpoint that function ended, so that sent message order is enforceable by await
        return


    async def relayAddChannel(self, ctx, channel, toChanId, webhookUrl, attachsAsUrl, userProfiles):
        # Retrieve stored data
        msgrelayStoreV2 = await self.config.guild(ctx.guild).msgrelayStoreV2()
        # Append to data
        msgrelayStoreV2[str(channel.id)] = {
            "toWebhook": str(webhookUrl),
            # "toChanId": str(toChanId),
            "attachsAsUrl": bool(attachsAsUrl),
            "userProfiles": bool(userProfiles),
        }
        # Push changes
        await self.config.guild(ctx.guild).msgrelayStoreV2.set(msgrelayStoreV2)
        return True

    async def relayRemoveChannel(self, ctx, channel):
        # Retrieve stored data
        msgrelayStoreV2 = await self.config.guild(ctx.guild).msgrelayStoreV2()
        # Remove from data
        msgrelayStoreV2.pop(str(channel.id), None)
        # Push changes
        await self.config.guild(ctx.guild).msgrelayStoreV2.set(msgrelayStoreV2)
        return True

    async def timestampEmbed(self, ctx, utcTimeObj):
        embedColor = await ctx.embed_colour()
        embed = discord.Embed(color=embedColor, timestamp=utcTimeObj)
        embed.set_footer(text='\u200b')
        return embed

    async def webhookFinder(self, channel):
        # Find a webhook that the bot made
        try:
            whooklist = await channel.webhooks()
        except:
            return False
        # Return if match
        for wh in whooklist:
            if self.bot.user == wh.user:
                return wh.url
        # If the function got here, it means there isn't one that the bot made
        try:
            newHook = await channel.create_webhook(name="Webhook")
            return newHook.url
        # Could not create webhook, return False
        except:
            return False


    # Bot Commands

    @commands.group()
    @checks.guildowner_or_permissions(administrator=True)
    async def msgrelay(self, ctx: commands.Context):
        """Set message relays

        Message relays allow you to forward messages to another server via a webhook.

        *v2 released with breaking changes on 29 Jun 2021.*
        *Old data saved under `v1` command.*
        *[Join the Support Discord for announcements and more info](https://coffeebank.github.io/discord)*"""
        if not ctx.invoked_subcommand:
            msgrelayStoreV2 = await self.config.guild(ctx.guild).msgrelayStoreV2()
            relayList = ""
            for relayId in msgrelayStoreV2:
                relayList += f"**<#{relayId}>**\n{msgrelayStoreV2[relayId]}\n\n"
            eg = discord.Embed(color=(await ctx.embed_colour()), title="Message Relays in this Server", description=relayList)
            await ctx.send(embed=eg)

    @msgrelay.command(name="add", aliases=["edit"])
    async def mmmradd(self, ctx, fromChannel: discord.TextChannel, toWebhook: str):
        """Create a message relay
        
        Currently only supports webhook urls. [How to create webhooks.](https://support.discord.com/hc/article_attachments/1500000463501/Screen_Shot_2020-12-15_at_4.41.53_PM.png)
        *[Help us develop support for #channels >](https://coffeebank.github.io/discord)*"""
        if "https://" not in toWebhook:
            return await ctx.send("Invalid webhook URL. Create a webhook for the channel you want to send to. https://support.discord.com/hc/article_attachments/1500000463501/Screen_Shot_2020-12-15_at_4.41.53_PM.png")

        # toChannel support coming soon(tm), help is welcome
        # if "https://" not in toWebhook:
        #     toWebhook = await self.webhookFinder(toWebhook)
        #     if toWebhook == False:
        #         return await ctx.send("Error creating webhook. Do I have \"Manage Webhooks\" permissions?")

        # Set userProfiles
        userProfiles = await ctx.send("Do you want messages to be forwarded with usernames and profile pics?")
        start_adding_reactions(userProfiles, ReactionPredicate.YES_OR_NO_EMOJIS)
        userProfilesPred = ReactionPredicate.yes_or_no(userProfiles, ctx.author)
        await ctx.bot.wait_for("reaction_add", check=userProfilesPred)

        # Set attachsAsUrl
        attachsAsUrl = await ctx.send("Do you want attachments (images) to be forwarded as image links? (is faster, but deleted images will fail to load)")
        start_adding_reactions(attachsAsUrl, ReactionPredicate.YES_OR_NO_EMOJIS)
        attachsAsUrlPred = ReactionPredicate.yes_or_no(attachsAsUrl, ctx.author)
        await ctx.bot.wait_for("reaction_add", check=attachsAsUrlPred)

        # Save
        await self.relayAddChannel(ctx, fromChannel, toChanId=None, webhookUrl=toWebhook, userProfiles=userProfilesPred.result, attachsAsUrl=attachsAsUrlPred.result)
        try:
            await fromChannel.send("**This channel's contents are now being forwarded!**\nThis is a sample message.")
        except:
            return await ctx.send("Setup was completed, but some permissions may be missing.")
        await ctx.message.add_reaction("✅")

    @msgrelay.command(name="delete", aliases=["remove"])
    async def mmmrdelete(self, ctx, fromChannel: discord.TextChannel):
        """Delete a message relay
        
        Input: #channels"""
        await self.relayRemoveChannel(ctx, fromChannel)
        await ctx.message.add_reaction("✅")

    @commands.command(aliases=["msgmove"])
    @checks.mod()
    async def msgcopy(self, ctx, fromChannel: discord.TextChannel, toChannel: discord.TextChannel, maxMessages:int, skipMessages:int=0):
        """Copies messages from one channel to another
        
        Retrieve 'maxMessages' number of messages from history, and optionally discard 'skipMessages' number of messages from the retrieved list.
        
        Retrieving more than 10 messages will result in Discord ratelimit throttling, so please be patient.
        
        Requires webhook permissions."""
        await ctx.message.add_reaction("⏳")

        toWebhook = await self.webhookFinder(toChannel)
        if toWebhook == False:
            return await ctx.send("Error trying to create webhook at destination channel.")

        # Start webhook session
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(toWebhook, adapter=AsyncWebhookAdapter(session))

            # Retrieve messages, sorted by oldest first
            msgList = await fromChannel.history(limit=maxMessages).flatten()
            msgList.reverse()
            if skipMessages > 0:
                if skipMessages >= maxMessages:
                    return await ctx.send("Cannot skip more messages than the max number of messages you are retrieving.")
                # https://stackoverflow.com/a/37105499
                msgList = msgList[:-skipMessages or None]

            # Send them via webhook
            msgItemLast = msgList[0].created_at
            for msgItem in msgList:
                # Send timestamp if it's been more than 10mins time difference
                # If they equal, it means it's the first item, so send timestamp
                if msgItemLast == msgItem.created_at or (msgItem.created_at-msgItemLast).total_seconds() > 600:
                    await webhook.send(
                        username="\u17b5\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u17b5",
                        avatar_url='https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/0-Background.svg/300px-0-Background.svg.png',
                        embed=await self.timestampEmbed(ctx, msgItem.created_at)
                    )
                try:
                    await self.msgFormatter(webhook, msgItem)
                except:
                    await ctx.send("Failed to send: "+str(msgItem))
                # Save timestamp to msgItemLast
                msgItemLast = msgItem.created_at

        # Add react on complete
        await ctx.message.add_reaction("✅")

    # Listeners

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore message if it's a webhook
        # REQUIRED IF TWO-WAY CHAT REDIRECTS
        # TO STOP A TWO-WAY REDIRECT, USE [p]msgrelay delete #channel
        if message.webhook_id:
            return
        # only do anything if message is sent in a guild
        if message.guild:
            relayStore = await self.config.guild(message.guild).msgrelayStoreV2()
            # Retrieve webhook info from channel store
            if str(message.channel.id) in relayStore:
                toWebhook = relayStore[str(message.channel.id)]["toWebhook"]
                attachsAsUrl = relayStore[str(message.channel.id)]["attachsAsUrl"]
                userProfiles = relayStore[str(message.channel.id)]["userProfiles"]
                # Send along webhook
                async with aiohttp.ClientSession() as session:
                    webhook = Webhook.from_url(toWebhook, adapter=AsyncWebhookAdapter(session))
                    await self.msgFormatter(webhook, message, attachsAsUrl=attachsAsUrl, userProfiles=userProfiles)
            else:
                return
        else:
            return


    # Legacy Commands
    @msgrelay.group(name="v1")
    @checks.is_owner()
    async def msgrelayV1(self, ctx: commands.Context):
        """View legacy data

        Settings will not be modifiable, and it is encouraged to migrate to v2.

        The new v2 shifts data from being under the Bot Owner to separate guilds, and allows guild owners to create their own relays.
        
        Because of this change, the old settings are incompatible with the new settings."""
        if not ctx.invoked_subcommand:
            msgrelayStore = await self.config.msgrelayStore()
            relayList = ""
            for relayId in msgrelayStore:
                relayList += f"**<#{relayId}>**\n{msgrelayStore[relayId]}\n\n"
            eg = discord.Embed(color=(await ctx.embed_colour()), title="Legacy Relays (no longer work)", description=relayList)
            await ctx.send(embed=eg)
    @msgrelayV1.command(name="reset")
    async def mmmrV1reset(self, ctx, areYouSure: bool):
        """⚠️ Deletes all V1 relays
        
        Type **`[p]msgrelay reset True`** if you're absolutely sure."""
        if areYouSure == True:
            await self.config.msgrelayChannels.set([])
            await self.config.msgrelayStore.set({})
            await ctx.message.add_reaction("✅")
