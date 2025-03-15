import asyncio
import json

import discord
from discord import Embed, Webhook
import aiohttp

import logging
logger = logging.getLogger(__name__)


# Utility Commands

async def validateWebhookInput(self, ctx, userInput: str):
    toWebhook = userInput
    # Only check for alias if command is run in a guild
    # 2025-03-15: Doesn't work in DMs, asks for "Manage Webhooks" permissions
    if ctx.guild:
        # Check if it is an alias
        webhookAlias = await self.config.guild(ctx.guild).webhookAlias()
        if userInput in webhookAlias:
            toWebhook = webhookAlias.get(userInput, None)
    if "https://" not in toWebhook:
        raise commands.UserInputError("Error: Invalid webhook URL")
    else:
        return toWebhook


# Engines

async def sendhookEngine(toWebhook, content=None, attachments=None, embeds=None, webhookUser=None, webhookAvatar=None):
    # Start webhook session
    try:
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(toWebhook, session=session)

            # Check for attachments
            if attachments:
                # Send message first if there is a message
                # 2025-03-15: AttributeError: 'dict' object has no attribute 'to_dict'
                if content is not None:
                    await webhook.send(
                        content,
                        embeds=([discord.Embed.from_dict(e) for e in embeds] if embeds else []),
                        username=webhookUser,
                        avatar_url=webhookAvatar
                    )
                # Then send each attachment in separate messages
                for msgAttach in attachments:
                    try:
                        await webhook.send(
                            username=webhookUser,
                            avatar_url=webhookAvatar,
                            file=await msgAttach.to_file()
                        )
                    except Exception:
                        # Couldn't send, retry sending file as url only
                        await webhook.send(
                            "File: "+str(msgAttach.url), 
                            username=webhookUser,
                            avatar_url=webhookAvatar
                        )
            else:
                # 2025-03-15: AttributeError: 'dict' object has no attribute 'to_dict'
                await webhook.send(
                    content,
                    embeds=([discord.Embed.from_dict(e) for e in embeds] if embeds else []),
                    username=webhookUser,
                    avatar_url=webhookAvatar
                )
    except Exception as err:
        logger.error(err, exc_info=True)
        raise err
    finally:
        await session.close()


async def edithookEngine(toWebhook, messageIdToEdit, content=None, attachments=None, embeds=None):
    # Start webhook session
    async with aiohttp.ClientSession() as session:
        try:
            webhook = Webhook.from_url(toWebhook, session=session)
            messageAttributes = {
                "message_id": messageIdToEdit,
                "content": content,
                "attachments": attachments,
            }
            # 2025-03-15: Support deleting the embeds by sending []
            if embeds:
                # AttributeError: 'dict' object has no attribute 'to_dict'
                messageAttributes["embeds"] = [discord.Embed.from_dict(e) for e in embeds]
            # "if embeds" returns False for []
            elif embeds == []:
                messageAttributes["embeds"] = []
            else:
                messageAttributes["embeds"] = None
            # Remove Nones before sending
            await webhook.edit_message(**{key: value for key, value in messageAttributes.items() if value is not None})
        except Exception as err:
            logger.error(err, exc_info=True)
            raise err
        finally:
            await session.close()
