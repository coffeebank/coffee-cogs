import asyncio

from redbot.core.utils.predicates import ReactionPredicate
from redbot.core.utils.menus import start_adding_reactions
import discord

from .utils import webhookSettings, webhookFinder

import logging
logger = logging.getLogger(__name__)


relayGetData = webhookSettings


async def relayAddChannel(self, ctx, chanObj, toWebhook):
    msgrelayStoreV2 = await self.config.guild(ctx.guild).msgrelayStoreV2()
    
    # Set attachsAsUrl
    attachsAsUrl = await ctx.send("Do you want attachments (images) to be forwarded as links?\n> **Yes:** Images will be sent as links\n> **No:** Images will be re-uploaded as a new file")
    start_adding_reactions(attachsAsUrl, ReactionPredicate.YES_OR_NO_EMOJIS)
    attachsAsUrlPred = ReactionPredicate.yes_or_no(attachsAsUrl, ctx.author)
    try:
        await ctx.bot.wait_for("reaction_add", timeout=30, check=attachsAsUrlPred)
    except asyncio.TimeoutError:
        return False

    # Set userProfiles
    userProfiles = await ctx.send("Do you want messages to be forwarded with profiles?\n> **Yes:** Messages will be forwarded with usernames and profile pics\n> **No:** Messages will use the webhook's name and image instead")
    start_adding_reactions(userProfiles, ReactionPredicate.YES_OR_NO_EMOJIS)
    userProfilesPred = ReactionPredicate.yes_or_no(userProfiles, ctx.author)
    try:
        await ctx.bot.wait_for("reaction_add", timeout=30, check=userProfilesPred)
    except asyncio.TimeoutError:
        return False

    # Create data store
    try:
        relayInfo = {
            "toWebhook": str(toWebhook),
            "attachsAsUrl": attachsAsUrlPred.result,
            "userProfiles": userProfilesPred.result,
        }
    except Exception as err:
        logger.error(f"relayAddChannel: Creating relay info failed: {err}")
        return False

    # Append to data
    try:
        msgrelayStoreV2[str(chanObj.id)].append(relayInfo)
    except KeyError:
        msgrelayStoreV2[str(chanObj.id)] = [relayInfo]
    except Exception as err:
        logger.error(f"relayAddChannel: Saving data failed: {err}")
        return False

    # Return changes
    return msgrelayStoreV2


async def relayRemoveChannel(self, ctx, channel, itemToDelete):
    # Retrieve stored data
    msgrelayStoreV2 = await self.config.guild(ctx.guild).msgrelayStoreV2()

    # Remove from data
    if itemToDelete <= 0:
        msgrelayStoreV2.pop(str(channel.id), None)
    else:
        # Zero-indexed
        msgrelayStoreV2[str(channel.id)].pop(itemToDelete-1)

    # Push changes
    await self.config.guild(ctx.guild).msgrelayStoreV2.set(msgrelayStoreV2)
    return True


async def relayCheckInput(self, ctx, toChannel):
    # Find/create webhook at destination if input is a channel
    if isinstance(toChannel, discord.TextChannel):
        toWebhook = await webhookFinder(self, toChannel)
        if toWebhook == False:
            await ctx.send("An error occurred: could not create webhook. Am I missing permissions?")
            return False
        return toWebhook
    # Use webhook url as-is if there is https link (doesn't have to be Discord)
    if "https://" in toChannel:
        return str(toChannel)
    # Error likely occurred, return False
    await ctx.send("Error: Channel is not in this server, or webhook URL is invalid.\n\nIf you're trying to move messages across servers, please create a Webhook in the channel you want to send to: https://support.discord.com/hc/article_attachments/1500000463501/Screen_Shot_2020-12-15_at_4.41.53_PM.png")
    return False



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
