import asyncio
import aiohttp
import json
import typing

from redbot.core import Config, commands, checks
from redbot.core.utils.predicates import ReactionPredicate
from redbot.core.utils.menus import start_adding_reactions
import discord
from discord import Webhook, SyncWebhook
import requests

from .utils import msgFormatter, webhookSettings, webhookFinder, WEBHOOK_EMPTY_AVATAR, WEBHOOK_EMPTY_NAME
from .utils_copy import timestampEmbed
from .utils_relay import relayGetData, relayAddChannel, relayRemoveChannel, relayCheckInput

import logging
logger = logging.getLogger(__name__)


class Msgmover(commands.Cog):
    """Move messages around, cross-channels, cross-server!
    
    Run `[p]msgmover` to see more details!

    msgcopy: Copy a set # of past messages to another channel/server
    msgrelay: Forward all of a channel's messages to another channel/server
    """

    def __init__(self, bot):
        self.config = Config.get_conf(self, identifier=806715409318936616)
        self.bot = bot
        default_guild = {
            "msgrelayStoreV2": {},
            "relayTimer": 20,
        }
        """
            "msgrelayStoreV2": {
                "chanId": [
                    {
                        "toWebhook": str,
                        "pref": bool,
                        "pref": bool,
                    },
                ],
            }
        """
        self.config.register_guild(**default_guild)

    # This cog does not store any End User Data
    async def red_get_data_for_user(self, *, user_id: int):
        return {}
    async def red_delete_data_for_user(self, *, requester, user_id: int) -> None:
        pass


    # Bot Commands

    @commands.group()
    @commands.has_permissions(manage_messages=True)
    async def msgmover(self, ctx: commands.Context):
        """Hi! Thanks for installing msgmover!

        Msgmover comes with two key features, both of which use webhooks to move messages from one place to another with a close-to-native feel:

        **`[p]msgcopy`** - Copies a set # of messages from one channel to another *(single-use)*
        - *Requires users with **Manage Messages** permissions*

        **`[p]msgrelay`** - Forward messages to other channels/servers *(continuous)*
        - *Requires server admins with **Administrator** permissions*

        Need help? [Reach us in our Support Discord >](https://coffeebank.github.io/discord)
        """
        if not ctx.invoked_subcommand:
            pass


    @commands.command(aliases=["msgmove"])
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(add_reactions=True, read_message_history=True)
    async def msgcopy(self, ctx, fromChannel: discord.TextChannel, toChannel: typing.Union[discord.TextChannel, str], maxMessages:int, skipMessages:int=0):
        """Copies messages from one channel to another

        toChannel can either be a #channel or a webhook URL.
        
        Retrieve 'maxMessages' number of messages from history, and optionally discard 'skipMessages' number of messages from the retrieved list.
        
        Retrieving more than 10 messages will result in Discord ratelimit throttling, so please be patient.
        
        *Errors? Please [help us by reporting them in our Support Discord >](https://coffeebank.github.io/discord)*
        """

        # Error catching
        toWebhook = await relayCheckInput(self, ctx, toChannel)
        if toWebhook == False:
            return

        if maxMessages <= 0:
            return await ctx.send("Error: Please input a valid number of messages to copy.")
        if skipMessages >= maxMessages:
            return await ctx.send("Error: Cannot skip more messages than the max number of messages you are retrieving.")

        # Start webhook session
        await ctx.message.add_reaction("⏳")
        webhook = SyncWebhook.from_url(toWebhook)

        # Retrieve messages, sorted by oldest first
        # Can't use oldest_first= since that will only return earliest messages in channel, instead of what we want
        msgList = [message async for message in fromChannel.history(limit=maxMessages)]
        msgList.reverse()
        if skipMessages > 0:
            # https://stackoverflow.com/a/37105499
            msgList = msgList[:-skipMessages or None]

        # Send them via webhook
        msgItemLast = msgList[0].created_at
        for msgItem in msgList:
            # Send timestamp if it's been more than 10mins time difference
            # If they equal, it means it's the first item, so send timestamp
            if msgItemLast == msgItem.created_at or (msgItem.created_at-msgItemLast).total_seconds() > 600:
                webhook.send(
                    username=WEBHOOK_EMPTY_NAME,
                    avatar_url=WEBHOOK_EMPTY_AVATAR,
                    embed=await timestampEmbed(self, ctx, msgItem.created_at)
                )
                await asyncio.sleep(1)
            configJson = webhookSettings({"attachsAsUrl": False, "userProfiles": True})
            whMsg = await msgFormatter(self, webhook, msgItem, configJson)
            if whMsg == False:
                await ctx.send("Failed to send: "+str(msgItem))
            else:
                # Trigger edited tag if it was edited
                if msgItem.edited_at:
                    await msgFormatter(self, webhook, msgItem, configJson, editMsgId=whMsg.id)
            # Save timestamp to msgItemLast
            msgItemLast = msgItem.created_at

        # Add react on complete
        try:
            await ctx.message.add_reaction("✅")
        except discord.NotFound:
            await ctx.send("Done!")


    @commands.group()
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(add_reactions=True, embed_links=True)
    async def msgrelay(self, ctx: commands.Context):
        """Create message relays

        Forward new messages to another server via a webhook - as if you created a portal between the two chats.
        
        (Also works with Discord-webhook-compatible bridges for other chat apps.)

        *[Join the Support Discord for announcements and more info](https://coffeebank.github.io/discord)*"""
        if not ctx.invoked_subcommand:
            # Message Relays
            msgrelayStoreV2 = await self.config.guild(ctx.guild).msgrelayStoreV2()
            relayList = ""
            for relayId in msgrelayStoreV2:
                relayList += f"**<#{relayId}>**\n{str(msgrelayStoreV2[relayId])}\n\n"
            eg = discord.Embed(color=(await ctx.embed_colour()), title="Message Relays in this Server", description=str(relayList)[:4090])
            await ctx.send(embed=eg)
            # Relay settings
            es = discord.Embed(color=(await ctx.embed_colour()), title="Message Relay Settings in this Server")
            es.add_field(name="Relay Timer", value=await self.config.guild(ctx.guild).relayTimer(), inline=True)
            await ctx.send(embed=es)

    @msgrelay.command(name="add")
    async def mmmradd(self, ctx, fromChannel: discord.TextChannel, toChannel: typing.Union[discord.TextChannel, str]):
        """Create a message relay
        
        Cross-server relays must be a webhook. [How to create webhooks >](https://support.discord.com/hc/article_attachments/1500000463501/Screen_Shot_2020-12-15_at_4.41.53_PM.png)"""

        # Error catching
        relayResp = await relayCheckInput(self, ctx, toChannel)
        if relayResp == False:
            return

        # Create entry
        relayAdd = await relayAddChannel(self, ctx, fromChannel, relayResp)
        if relayAdd == False:
            return await ctx.send("Setup was stopped. Exited.")
        else:
            await self.config.guild(ctx.guild).msgrelayStoreV2.set(relayAdd)

        # Test
        try:
            await fromChannel.send("**Channels are now linked!**\nThis is a sample message.")
        except:
            return await ctx.send("Setup was successfully completed, but some permissions may be missing.")
        await ctx.message.add_reaction("✅")

    @msgrelay.command(name="edit")
    async def mmmredit(self, ctx, fromChannel: discord.TextChannel, itemToEdit: int, toChannel):
        """Edit a message relay
        
        Currently only supports webhook urls. [How to create webhooks.](https://support.discord.com/hc/article_attachments/1500000463501/Screen_Shot_2020-12-15_at_4.41.53_PM.png)
        *[Help us develop support for #channels >](https://coffeebank.github.io/discord)*"""
        # Error catching
        relayResp = await relayCheckInput(self, ctx, toChannel)
        if relayResp == False:
            return

        # Ask for input and have it successfully complete before deleting old entry
        relayAdd = await relayAddChannel(self, ctx, fromChannel, relayResp)
        if relayAdd == False:
            return await ctx.send("Setup was stopped. Exited.")
        else:
            # Create new entry
            await self.config.guild(ctx.guild).msgrelayStoreV2.set(relayAdd)
            # Delete old entry
            await relayRemoveChannel(self, ctx, fromChannel, itemToEdit)

        # Test
        try:
            await fromChannel.send("**Channels are now linked!**\nThis is a sample message.")
        except:
            return await ctx.send("Setup was successfully completed, but some permissions may be missing.")
        await ctx.message.add_reaction("✅")

    @msgrelay.command(name="delete", aliases=["remove"])
    async def mmmrdelete(self, ctx, fromChannel: discord.TextChannel, itemToDelete: int):
        """Delete a message relay
        
        fromChannel: the originating #channel
        itemToDelete: put 1, 2, ... for which one you want to delete.
        
        To delete all relays for a fromChannel, set itemToDelete to 0 (zero)."""
        result = await relayRemoveChannel(self, ctx, fromChannel, itemToDelete)
        if result == False:
            return await ctx.send("Deletion failed. Please report this error to the support server at <https://coffeebank.github.io/discord>.")
        await ctx.message.add_reaction("✅")

    @msgrelay.command(name="settimer")
    async def mmmrsettimer(self, ctx, seconds: int):
        """Seconds after the relay checks for edited/deleted messages
        
        To disable checking for edits/deleted messages after sending, set seconds to 0 (zero)."""
        await self.config.guild(ctx.guild).relayTimer.set(seconds)
        await ctx.message.add_reaction("✅")

    @commands.command()
    async def msgcount(self, ctx):
        """Find how many messages it has been after a message
        
        Reply to a message to use this command."""
        if ctx.message.reference:
            await ctx.message.add_reaction("⏳")
            messages = [message async for message in ctx.channel.history(limit=None, after=ctx.message.reference.resolved)]
            await ctx.message.add_reaction("✅")
            return await ctx.send(str(len(messages))+" + 2 (your bot command and this message)")
        else:
            return await ctx.send("Please reply to a message to use this command!")


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
                hookData = relayStore[str(message.channel.id)]
                relayTimer = await self.config.guild(message.guild).relayTimer()
                # Migrate data to multi-hook support if needed
                try:
                    assert isinstance(hookData, list)
                except AssertionError:
                    hookData = await self.fixMsgrelayStoreV2alpha(message)
                # Send along webhook for each in array
                for wh in hookData:
                    configJson = relayGetData(wh)
                    webhook = SyncWebhook.from_url(wh["toWebhook"])
                    whResult = await msgFormatter(self, webhook, message, configJson)
                    wh["whResult"] = whResult.id
                # Wait, then check for edits/deletes
                if relayTimer <= 0:
                    return
                else:
                    await asyncio.sleep(relayTimer)
                    try:
                        endMsg = await message.channel.fetch_message(message.id)
                    except discord.NotFound:
                        for wf in hookData:
                            configJson = relayGetData(wh)
                            webhook = SyncWebhook.from_url(wf["toWebhook"])
                            await msgFormatter(self, webhook, message, configJson, deleteMsgId=wf.get("whResult", None))
                    else:
                        if endMsg.edited_at:
                            for wf in hookData:
                                configJson = relayGetData(wh)
                                webhook = SyncWebhook.from_url(wf["toWebhook"])
                                await msgFormatter(self, webhook, endMsg, configJson, editMsgId=wf.get("whResult", None))
            else:
                return
        else:
            return


    # Legacy Commands

    async def fixMsgrelayStoreV2alpha(self, ctx):
        oldData = await self.config.guild(ctx.guild).msgrelayStoreV2()
        if isinstance(oldData[str(ctx.channel.id)], list) == False:
            newData = [oldData[str(ctx.channel.id)]]
            oldData[str(ctx.channel.id)] = newData
            await self.config.guild(ctx.guild).msgrelayStoreV2.set(oldData)
            return newData
        else:
            return oldData[str(ctx.channel.id)]

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
