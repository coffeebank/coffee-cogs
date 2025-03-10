import asyncio
import aiohttp
import typing

from redbot.core import Config, commands
import discord
from discord import Webhook

from .utils import msgFormatter, webhookSettings, webhookFinder, WEBHOOK_EMPTY_AVATAR, WEBHOOK_EMPTY_NAME
from .utils_copy import timestampEmbed
from .utils_relay import relayGetData, relayAddChannel, relayRemoveChannel, relayCheckInput, fixMsgrelayStoreV2alpha

import logging
logger = logging.getLogger(__name__)


class Msgmover(commands.Cog):
    """Move messages around, cross-channels, cross-server!
    
    Msgmover comes with two key features, both of which use webhooks to move messages from one place to another with a close-to-native feel:

    **`[p]msgcopy`** - Copies a set # of messages from one channel to another *(single-use)*
    - *Requires users with **Manage Messages** permissions*

    **`[p]msgrelay`** - Forward new messages to other channels/servers *(continuous)*
    - *Requires server admins with **Administrator** permissions*

    Need help? [Reach us in our Support Discord >](https://coffeebank.github.io/discord)
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



    # msgcopy

    @commands.command(name="msgcopy", aliases=["msgmove", "msgmover"])
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(add_reactions=True, read_message_history=True)
    async def msgcopy(self, ctx, fromChannel: discord.TextChannel, toChannel: typing.Union[discord.TextChannel, str], maxMessages:int, skipMessages:int=0):
        """Copies messages from one channel to another

        toChannel can either be a #channel or a webhook URL.
        
        Retrieve 'maxMessages' number of messages from history, and optionally discard 'skipMessages' number of messages from the retrieved list.
        
        Retrieving more than 10 messages will result in Discord ratelimit throttling, so please be patient.
        
        - *Errors? Please [help us by reporting them in our Support Discord >](https://coffeebank.github.io/discord)*
        - *See all commands:* **`[p]help Msgmover`**"""

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
        try:
            async with aiohttp.ClientSession() as session:
                webhook = Webhook.from_url(toWebhook, session=session)

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
                        await webhook.send(
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
        finally:
            await session.close()

    @commands.command(name="msgcount")
    @commands.bot_has_permissions(add_reactions=True)
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


    # msgrelay

    @commands.group(name="msgrelay")
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(add_reactions=True, embed_links=True)
    async def msgrelay(self, ctx: commands.Context):
        """Forward new messages to other channels/servers

        Create message relays - as if a portal connects the two chats.

        Have two-way conversations across 2+ servers at once!
        
        *[Join the Support Discord for announcements and more info](https://coffeebank.github.io/discord)*"""
        if not ctx.invoked_subcommand:
            pass

    @msgrelay.command(name="settings")
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(embed_links=True)
    async def mmmrsettings(self, ctx):
        """See relay settings (⚠️ Sensitive info)
        """
        # Message Relays
        msgrelayStoreV2 = await self.config.guild(ctx.guild).msgrelayStoreV2()
        relayList = ""
        for relayId in msgrelayStoreV2:
            relayList = f"**<#{relayId}>**\n{str(msgrelayStoreV2[relayId])}\n\n"
            eg = discord.Embed(color=(await ctx.embed_colour()), description=str(relayList)[:4090])
            await ctx.send(embed=eg)
        # Relay settings
        es = discord.Embed(color=(await ctx.embed_colour()), title="Message Relay Settings in this Server")
        es.add_field(name="Relay Timer", value=await self.config.guild(ctx.guild).relayTimer(), inline=True)
        await ctx.send(embed=es)

    @msgrelay.command(name="add")
    @commands.bot_has_permissions(add_reactions=True)
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
        except Exception as err:
            logger.error(err)
            return await ctx.send("Setup was successfully completed, but some permissions may be missing.")
        await ctx.message.add_reaction("✅")

    @msgrelay.command(name="edit")
    @commands.bot_has_permissions(add_reactions=True)
    async def mmmredit(self, ctx, fromChannel: discord.TextChannel, itemToEdit: int, toChannel: typing.Union[discord.TextChannel, str]):
        """Edit a message relay
        
        fromChannel: the originating #channel
        itemToEdit: put 1, 2, ... for which one you want to delete. (check `[p]msgrelay settings` for list of relays from each channel)
        
        Currently only supports webhook urls. [How to create webhooks.](https://support.discord.com/hc/article_attachments/1500000463501/Screen_Shot_2020-12-15_at_4.41.53_PM.png)
        *[Help us develop support for #channels >](https://coffeebank.github.io/discord)*"""

        # Error catching
        if itemToEdit <= 0:
            return await ctx.send("Error: If there's only one relay in the channel, please use 1 for itemToEdit.")
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
        except Exception as err:
            logger.error(err)
            return await ctx.send("Setup was successfully completed, but some permissions may be missing.")
        await ctx.message.add_reaction("✅")

    @msgrelay.command(name="delete", aliases=["remove"])
    @commands.bot_has_permissions(add_reactions=True)
    async def mmmrdelete(self, ctx, fromChannel: discord.TextChannel, itemToDelete: int):
        """Delete a message relay
        
        fromChannel: the originating #channel
        itemToDelete: put 1, 2, ... for which one you want to delete. (check `[p]msgrelay settings` for list of relays from each channel)
        
        To delete all relays for a fromChannel, set itemToDelete to 0 (zero)."""
        result = await relayRemoveChannel(self, ctx, fromChannel, itemToDelete)
        if result == False:
            return await ctx.send("Deletion failed. Please report this error to the support server at <https://coffeebank.github.io/discord>.")
        await ctx.message.add_reaction("✅")

    @msgrelay.command(name="settimer")
    @commands.bot_has_permissions(add_reactions=True)
    async def mmmrsettimer(self, ctx, seconds: int):
        """Seconds after the relay checks for edited/deleted messages
        
        To disable checking for edits/deleted messages after sending, set seconds to 0 (zero)."""
        await self.config.guild(ctx.guild).relayTimer.set(seconds)
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
        if not message.guild:
            return

        # Retrieve webhook info from channel store
        relayStore = await self.config.guild(message.guild).msgrelayStoreV2()
        if not str(message.channel.id) in relayStore:
            return

        hookData = relayStore[str(message.channel.id)]
        relayTimer = await self.config.guild(message.guild).relayTimer()
        
        # Migrate data to multi-hook support if needed
        try:
            assert isinstance(hookData, list)
        except AssertionError:
            hookData = await fixMsgrelayStoreV2alpha(self, message)

        # Send along webhook for each in array
        try:
            async with aiohttp.ClientSession() as session:
                for wh in hookData:
                    configJson = relayGetData(wh)
                    webhook = Webhook.from_url(wh["toWebhook"], session=session)
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
                            webhook = Webhook.from_url(wf["toWebhook"], session=session)
                            await msgFormatter(self, webhook, message, configJson, deleteMsgId=wf.get("whResult", None))
                    else:
                        if endMsg.edited_at:
                            for wf in hookData:
                                configJson = relayGetData(wh)
                                webhook = Webhook.from_url(wf["toWebhook"], session=session)
                                await msgFormatter(self, webhook, endMsg, configJson, editMsgId=wf.get("whResult", None))
        finally:
            await session.close()
