import asyncio
import aiohttp
import json
import textwrap

import discord

import logging
logger = logging.getLogger(__name__)


WEBHOOK_EMPTY_AVATAR = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/0-Background.svg/300px-0-Background.svg.png"
WEBHOOK_EMPTY_NAME = "\u2e33\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2e33"



async def msgFormatter(self, webhook, message, json, editMsgId=None, deleteMsgId=None):
    # webhook: A webhook object from discord.py
    # message: A message object from discord.py
    # json: A {dict} with config variables

    # Delete the message if it's delete
    if deleteMsgId is not None:
        try:
            return await webhook.delete_message(deleteMsgId)
        except:
            return False

    # Edit the message if it's edit
    if editMsgId is not None:
        try:
            return await webhook.edit_message(
                message_id=editMsgId,
                content=message.clean_content
            )
        except discord.HTTPException:
            return await webhook.edit_message(
                message_id=editMsgId,
                content="**Discord:** Unsupported content\n"+str(message.clean_content)
            )
        except:
            return False

    # Check for system messages, Set up user profile
    userProfilesName = None
    userProfilesAvatar = None
    if message.type == discord.MessageType.default or message.type == discord.MessageType.reply:
        msgContent = message.clean_content
        if json["userProfiles"] == True:
            # (dpy-v2) "Discord" is not allowed in webhook usernames
            userProfilesName = message.author.display_name.replace("Discord", "D🗪cord").replace("discord", "d🗪cord")
            userProfilesAvatar = message.author.display_avatar.url
    else:
        msgContent = "**Discord:** "+str(message.type)
        if json["userProfiles"] == True:
            userProfilesName = WEBHOOK_EMPTY_NAME
            userProfilesAvatar = WEBHOOK_EMPTY_AVATAR

    # Add reply if exists
    if message.reference and message.type == discord.MessageType.reply:
        # Retrieve replied-to message
        refObj = message.reference.resolved
        replyEmbed = discord.Embed(color=discord.Color(value=0x25c059), description="")

        # Fallback
        if hasattr(refObj, "clean_content") is False:
            refObj = message
            refContent = "Message not found"
            refUrl = ""
        else:
            refContent = refObj.clean_content
            refUrl = refObj.jump_url
        
        # Fill content
        if refContent:
            replyBody = (refContent[:56] + '...') if len(refContent) > 56 else refContent
        else:
            replyBody = "Click to see attachment 🖼️"
        # Create link to message
        replyTitle = f"↪️ {replyBody}"
        if json["userProfiles"] == True:
            replyEmbed.set_author(name=replyTitle, icon_url=refObj.author.display_avatar.url, url=refUrl)
        else:
            replyEmbed.set_author(name=replyTitle, url=refUrl)
        # Send this before the original message so that the embed appears above the message in chat
        await webhook.send(
            username=userProfilesName,
            avatar_url=userProfilesAvatar,
            embed=replyEmbed
        )
        await asyncio.sleep(1)
          

    # Add embed if exists
    msgEmbed = None
    # Do not set the embed if it came from a http link in the message (fixes repo issue #4)
    if message.embeds and "http" not in msgContent:
        msgEmbed = message.embeds

    # Add attachment if exists
    msgAttach = None
    if message.attachments:
        attachMaxSize = 10000000 # 10MB, prev. 25MB, prev. 8MB
        attachSuccess = False
        if json["attachsAsUrl"] == False:
            try:
                # attachMaxSize upload limit
                totalSize = 0
                for mm in message.attachments:
                    totalSize += mm.size
                assert totalSize < attachMaxSize
            except AssertionError:
                # See if each file is under attachMaxSize, maybe we can send individually
                for mm in message.attachments:
                    try:
                        assert mm.size < attachMaxSize
                        await webhook.send(
                            username=userProfilesName,
                            avatar_url=userProfilesAvatar,
                            files=[await mm.to_file()],
                            wait=True
                        )
                    except AssertionError:
                        await webhook.send(
                            content="**Discord:** File too large\n"+str(mm.url),
                            username=userProfilesName,
                            avatar_url=userProfilesAvatar,
                            wait=True
                        )
                attachSuccess = True
            else:
                msgAttach = [await msgA.to_file() for msgA in message.attachments]
                attachSuccess = True
        # Fallback if uploads don't work
        if json["attachsAsUrl"] == True or attachSuccess == False:
            for msgB in message.attachments:
                msgContent += "\n"+str(msgB.url)

    # Add activity if exists
    if message.activity:
        msgContent += f"\n**Discord:** Activity\n"+str(message.activity)
    if message.application:
        msgContent += f"\n**Discord:** {message.application.name}\n{message.application.description}"

    # Add sticker if exists
    if message.stickers:
        for msgSticker in message.stickers:
            if msgSticker.url is not None:
                msgContent += "\n"+str(msgSticker.url)
            else:
                msgContent += "\n**Discord:** Sticker\n"+str(msgSticker.name)+", "+str(msgSticker.id)

    # Send core message
    whMsg = False

    # (dpy-v2) Switch to argument unpacking, since passing None doesn't work anymore
    whMsgArgs = {}

    try:
        whMsgArgs = {
          "content": msgContent,
          "username": userProfilesName,
          "avatar_url": userProfilesAvatar,
          "embeds": msgEmbed,
          "files": msgAttach,
          "wait": True
        }
        whMsg = await webhook.send(
            **{k: v for k, v in whMsgArgs.items() if v is not None}
        )
    except discord.HTTPException:
        # catch HTTPException: 400 Bad Request (error code: 50035): Invalid Form Body
        #     In content: Must be 2000 or fewer in length.
        if len(msgContent) > 1964:
            msgLines = textwrap.wrap(msgContent, 2000, break_long_words=True)
            for msgLineItem in msgLines:
                whMsgArgs = {
                  "content": str(msgLineItem),
                  "username": userProfilesName,
                  "avatar_url": userProfilesAvatar,
                  "embeds": msgEmbed,
                  "files": msgAttach,
                  "wait": True
                }
                whMsg = await webhook.send(
                    **{k: v for k, v in whMsgArgs.items() if v is not None}
                )
        # catch HTTPException: 400 Bad Request (error code: 50006): Cannot send an empty message
        else:
            try:
                whMsgArgs = {
                  "content": "**Discord:** Unsupported content\n" + str(msgContent[:1964]) + (str(msgContent[1964:]) and '…'),
                  "username": userProfilesName,
                  "avatar_url": userProfilesAvatar,
                  "embeds": msgEmbed,
                  "files": msgAttach,
                  "wait": True
                }
                whMsg = await webhook.send(
                    **{k: v for k, v in whMsgArgs.items() if v is not None}
                )
            # One last try, without username or avatar
            except:
                whMsgArgs = {
                  "content": "**Discord:** Unsupported content\n" + str(msgContent[:1964]) + (str(msgContent[1964:]) and '…'),
                  "username": "Unknown User",
                  "embeds": msgEmbed,
                  "files": msgAttach,
                  "wait": True
                }
                whMsg = await webhook.send(
                    **{k: v for k, v in whMsgArgs.items() if v is not None}
                )
    except Exception as err:
        logger.error(err)
        # traceback.print_exc()
        return False
    
    # Need to tell endpoint that function ended, so that sent message order is enforceable by await
    return whMsg


def webhookSettings(json):
    """
    Default settings for sending webhooks
    """
    relayInfo = {
        "toWebhook": json.get("toWebhook", ""),
        "attachsAsUrl": json.get("attachsAsUrl", True),
        "userProfiles": json.get("userProfiles", True),
    }
    return relayInfo


async def webhookFinder(self, channel):
    # 2025-03-09 TODO: Update generic Exception to specific error cases

    # Find a webhook that the bot made
    try:
        whooklist = await channel.webhooks()
    except Exception as err:
        # Could not fetch webhooks, exit
        logger.error(err)
        return False
    # Fetch webhooks success, check for match
    for wh in whooklist:
        # Found match
        if self.bot.user == wh.user:
            return wh.url
    # If the function got here, it means there isn't one that the bot made
    try:
        newHook = await channel.create_webhook(name="Webhook")
        return newHook.url
    # Could not create webhook, return False
    except Exception as err:
        logger.error(err)
        return False
