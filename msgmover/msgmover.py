from redbot.core import Config, commands, checks
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

    async def red_get_data_for_user(self, *, user_id: int):
        # this cog does not story any data
        return {}

    async def red_delete_data_for_user(self, *, requester, user_id: int) -> None:
        # this cog does not story any data
        pass


    # Utility Commands

    async def msgFormatter(self, webhook, message, attachsAsUrl=False):
        # webhook: A webhook object from discord.py
        # message: A message object from discord.py
        # attachsAsUrl: Sets whether attachments should be linked using URLS, or re-uploaded as an independent file

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

        # Send core message
        try:
            await webhook.send(
                msgContent,
                username=message.author.display_name,
                avatar_url=message.author.avatar_url,
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


    async def relayAddChannel(self, channel, webhookUrl):
        # Retrieve stored data
        msgrelayChannels = await self.config.msgrelayChannels()
        msgrelayStore = await self.config.msgrelayStore()
        # Append to data
        msgrelayChannels.append(channel.id)
        msgrelayStore[str(channel.id)] = str(webhookUrl)
        # Push changes
        await self.config.msgrelayChannels.set(msgrelayChannels)
        await self.config.msgrelayStore.set(msgrelayStore)

    async def relayRemoveChannel(self, channel):
        # Retrieve stored data
        msgrelayChannels = await self.config.msgrelayChannels()
        msgrelayStore = await self.config.msgrelayStore()
        # Remove from data
        msgrelayChannels.remove(channel.id)
        msgrelayStore.pop(str(channel.id), None)
        # Push changes
        await self.config.msgrelayChannels.set(msgrelayChannels)
        await self.config.msgrelayStore.set(msgrelayStore)

    async def timestampEmbed(self, ctx, utcTimeObj):
        embedColor = await ctx.embed_colour()
        embed = discord.Embed(color=embedColor, timestamp=utcTimeObj)
        embed.set_footer(text='\u200b')
        return embed


    # Bot Commands

    @commands.group()
    @checks.is_owner()
    async def msgrelay(self, ctx: commands.Context):
        """Set message relays

        Message relays allow you to forward messages to another server via a webhook.

        (TODO: Automatically create the webhook if it doesn't exist)"""
        if not ctx.invoked_subcommand:
            pass

    @msgrelay.command(name="list")
    async def mmmrlist(self, ctx, fromChannel: discord.TextChannel=None):
        """List current settings"""
        if fromChannel == None:
            fromChannel = ctx.channel

        hooks = await fromChannel.webhooks()

        msgrelayChannels = await self.config.msgrelayChannels()
        msgrelayStore = await self.config.msgrelayStore()
        
        await ctx.send(str(fromChannel)+"'s webhooks: "+str(hooks)+"\n"+str(msgrelayChannels)+"\n"+str(msgrelayStore))

    @msgrelay.command(name="add")
    async def mmmradd(self, ctx, fromChannel: discord.TextChannel, toWebhook):
        """Create a message relay"""
        await self.relayAddChannel(fromChannel, toWebhook)
        await ctx.message.add_reaction("✅")

    @msgrelay.command(name="delete", aliases=["remove"])
    async def mmmrdelete(self, ctx, fromChannel: discord.TextChannel):
        """Delete a message relay"""
        await self.relayRemoveChannel(fromChannel)
        await ctx.message.add_reaction("✅")

    @msgrelay.command(name="reset")
    async def mmmrreset(self, ctx, areYouSure: bool):
        """⚠️ Deletes all relays
        
        Type **`[p]msgrelay reset True`** if you're absolutely sure."""
        if areYouSure == True:
            await self.config.msgrelayChannels.set([])
            await self.config.msgrelayStore.set({})
            await ctx.message.add_reaction("✅")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore message if it's a webhook
        # REQUIRED IF TWO-WAY CHAT REDIRECTS
        # TO STOP A TWO-WAY REDIRECT, USE [p]msgrelay delete #channel
        if message.webhook_id:
            return
        # only do anything if message is sent in a guild
        if message.guild:
            # Retrieve channel list and check channel ID
            channelList = await self.config.msgrelayChannels()
            channelId = message.channel.id
            # If channel is in channel list
            if channelId in channelList:
                # Retrieve webhook info from channel store
                channelStore = await self.config.msgrelayStore()
                toWebhook = channelStore[str(channelId)]
                # Send along webhook
                async with aiohttp.ClientSession() as session:
                    webhook = Webhook.from_url(toWebhook, adapter=AsyncWebhookAdapter(session))
                    await self.msgFormatter(webhook, message, attachsAsUrl=True)
            else:
                return
        else:
            return


    @commands.command()
    @checks.mod()
    async def msgcopy(self, ctx, fromChannel: discord.TextChannel, toWebhook, maxMessages: int=10):
        """Copies messages from one channel to another
        
        Uses a webhook to represent users
        Do not request more than 20 maxMessages"""
        await ctx.message.add_reaction("⏳")

        # Start webhook session
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(toWebhook, adapter=AsyncWebhookAdapter(session))

            # Retrieve messages, sorted by oldest first
            msgList = await fromChannel.history(limit=maxMessages).flatten()
            msgList.reverse()


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

