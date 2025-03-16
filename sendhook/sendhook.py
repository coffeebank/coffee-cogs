import asyncio
import json

from redbot.core import Config, commands
import discord
from discord import Webhook
import aiohttp

from .utils import *

import logging
logger = logging.getLogger(__name__)


class Sendhook(commands.Cog):
    """Send and edit webhook messages easily...
    
    To get started, send to a webhook URL using **`[p]sendhook`**

    You can set up aliases to mask the webhook URL, and make sending messages more convenient, using **`[p]aliashook`**

    The JSON commands support https://discohook.org message designs, including sending embeds.

    More details: [See FAQ & full documentation >](https://coffeebank.github.io/coffee-cogs/sendhook)

    -

    ⚠️ Webhook URLs are sensitive information. **Anyone can use them to send messages into your chat!** Please only run these commands in private guild channels.
    """

    def __init__(self):
        self.config = Config.get_conf(self, identifier=806715409318936616)
        default_guild = {
            "webhookAlias": {}
        }
        self.config.register_guild(**default_guild)

    # This cog does not store any End User Data
    async def red_get_data_for_user(self, *, user_id: int):
        return {}
    async def red_delete_data_for_user(self, *, requester, user_id: int) -> None:
        pass



    # Bot Commands

    @commands.guild_only()
    @commands.hybrid_group(name="aliashook")
    @commands.has_permissions(manage_guild=True, manage_webhooks=True)
    @commands.bot_has_permissions(manage_webhooks=True)
    async def aliashook(self, ctx: commands.Context):
        """Configure aliases for webhooks in your server

        -

        ⚠️ Webhook URLs are sensitive information. **Anyone can use them to send messages into your chat!** Please only run these commands in private guild channels.
        """
        if not ctx.invoked_subcommand:
            pass

    @aliashook.command(name="add", aliases=["edit"])
    @commands.has_permissions(manage_guild=True, manage_webhooks=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def ahadd(self, ctx, alias: str, webhook_url: str):
        """Add/update an alias for a webhook (⚠️ Sensitive info)
        
        To create an alias, you need a webhook URL.

        Create a webhook in Discord settings, or use **`[p]sendhooktools newhook`**

        -

        ⚠️ Webhook URLs are sensitive information. **Anyone can use them to send messages into your chat!** Please only run these commands in private guild channels. Once the bot receives your command, it will be deleted, for security purposes.
        """
        await friendlyReact(ctx, "⏳", "Loading ⏳")

        if "https://" not in webhook_url:
            return await ctx.send("Error: Invalid webhook URL")

        webhookAlias = await self.config.guild(ctx.guild).webhookAlias()
        webhookAlias[alias] = webhook_url
        await self.config.guild(ctx.guild).webhookAlias.set(webhookAlias)
        # Success
        await friendlyReact(ctx, "✅", "Done ✅")

    @aliashook.command(name="remove")
    @commands.has_permissions(manage_guild=True, manage_webhooks=True)
    async def ahremove(self, ctx, alias: str):
        """Remove an alias for a webhook"""
        webhookAlias = await self.config.guild(ctx.guild).webhookAlias()
        try:
            # Try to set alias to empty, before removing
            webhookAlias[alias] = ""
            del webhookAlias[alias]
            await self.config.guild(ctx.guild).webhookAlias.set(webhookAlias)
            # Success
            await friendlyReact(ctx, "✅", "Done ✅")
        except KeyError:
            pass

    @aliashook.command(name="list")
    @commands.has_permissions(manage_guild=True, manage_webhooks=True)
    async def ahlist(self, ctx, safe_mode: bool=True):
        """List all aliases for webhooks

        Safe Mode:
        - (Default) Send `True` to only include snippet (4 char.) Webhook URL.
        - Send `False` to include full Webhook URL.

        -

        ⚠️ Webhook URLs are sensitive information. **Anyone can use them to send messages into your chat!** Please only run these commands in private guild channels.
        """
        webhookAlias = await self.config.guild(ctx.guild).webhookAlias()

        # Exit if empty
        if len(webhookAlias.items()) <= 0:
            return await ctx.send("No webhook aliases found in this guild.")

        returntext = ""
        for name, url in webhookAlias.items():
            if safe_mode == True:
                returntext += "- "+name+" - …"+url[-4:]+"\n"
            else:
                returntext += "- "+name+" - ||"+url+"||\n"
        await ctx.send(returntext[:1999])

    @aliashook.command(name="show")
    @commands.has_permissions(manage_guild=True, manage_webhooks=True)
    async def ahshow(self, ctx, alias: str):
        """Show the saved webhook url for an alias (⚠️ Sensitive info)

        ⚠️ Webhook URLs are sensitive information. **Anyone can use them to send messages into your chat!** Please only run these commands in private guild channels.
        """
        webhookAlias = await self.config.guild(ctx.guild).webhookAlias()
        webhookData = webhookAlias.get(alias, None)
        if webhookData:
            await ctx.send("||"+webhookData[:1995]+"||")
        else:
            await ctx.send("Error: Couldn't fetch alias. Did you type it correctly?")


    @commands.hybrid_command()
    @commands.has_permissions(manage_webhooks=True)
    @commands.bot_has_permissions(manage_webhooks=True, embed_links=True)
    async def sendhook(self, ctx, webhook_url_or_alias: str, *, webhook_text: str, webhook_attachment: discord.Attachment=None):
        """Send a message through a webhook (⚠️ Sensitive info)
        
        You can set up aliases to mask the webhook URL, and make sending messages more convenient. For bot setup details, see **`[p]help Sendhook`**

        To send only an attachment (with no body), use **`_empty`** as your webhook_text.

        **Required user permissions:** Manage Webhooks.

        -
        
        ⚠️ Webhook URLs are sensitive information. **Anyone can use them to send messages into your chat!** Please only run these commands in private guild channels.
        
        Once the bot receives your command, it will be deleted, for security purposes.
        """
        await friendlyReact(ctx, "⏳", "Loading ⏳")

        # Check if it is an alias
        try:
            toWebhook = await validateWebhookInput(self, ctx, webhook_url_or_alias)
        except commands.UserInputError as err:
            return await ctx.send(err)

        # Error catching
        if webhook_text in ['_empty', ' ', '" "']:
            webhook_text = None
        webhook_attachments = ctx.message.attachments
        if ctx.interaction and webhook_attachment:
            webhook_attachments = [webhook_attachment]
        if not webhook_text and not webhook_attachments:
            # discord.HTTPException - 400 Bad Request (error code: 50006): Cannot send an empty message
            return await ctx.send("Error: Missing webhook_text. Did you mean to send some text, or upload an attachment?")

        # Send webhook
        try:
            await sendhookEngine(toWebhook, content=webhook_text, attachments=webhook_attachments)
        except ValueError as err:
            return await ctx.send("Error: "+str(err))
        except Exception as err:
            logger.error(err, exc_info=True)
            return await ctx.send("Oops, an error occurred :'( Please see bot logs for details...")
        else:
            # Success
            await friendlyReact(ctx, "✅", "Sent successfully. ✅")


    @commands.hybrid_command()
    @commands.has_permissions(manage_webhooks=True)
    @commands.bot_has_permissions(manage_webhooks=True, embed_links=True)
    async def sendhookself(self, ctx, webhook_url_or_alias: str, *, webhook_text: str=None, webhook_attachment: discord.Attachment=None):
        """Send a webhook as yourself (⚠️ Sensitive info)

        You can set up aliases to mask the webhook URL, and make sending messages more convenient. For bot setup details, see **`[p]help Sendhook`**

        **Required user permissions:** Manage Webhooks.

        -
        
        ⚠️ Webhook URLs are sensitive information. **Anyone can use them to send messages into your chat!** Please only run these commands in private guild channels.
        
        Once the bot receives your command, it will be deleted, for security purposes.
        """
        await friendlyReact(ctx, "⏳", "Loading ⏳")

        # Check if it is an alias
        try:
            toWebhook = await validateWebhookInput(self, ctx, webhook_url_or_alias)
        except commands.UserInputError as err:
            return await ctx.send(err)

        # Error catching
        if webhook_text in ['_empty', ' ', '" "']:
            webhook_text = None
        webhook_attachments = ctx.message.attachments
        if ctx.interaction and webhook_attachment:
            webhook_attachments = [webhook_attachment]
        if not webhook_text and not webhook_attachments:
            # discord.HTTPException - 400 Bad Request (error code: 50006): Cannot send an empty message
            return await ctx.send("Error: Missing webhook_text. Did you mean to send some text, or upload an attachment?")

        # Send webhook
        try:
            await sendhookEngine(toWebhook, content=webhook_text, attachments=webhook_attachments, webhookUser=ctx.message.author.display_name, webhookAvatar=ctx.message.author.display_avatar.url)
        except ValueError as err:
            return await ctx.send("Error: "+str(err))
        except Exception as err:
            logger.error(err, exc_info=True)
            return await ctx.send("Oops, an error occurred :'( Please see bot logs for details...")
        else:
            # Success
            await friendlyReact(ctx, "✅", "Done ✅")


    @commands.hybrid_command()
    @commands.has_permissions(manage_webhooks=True)
    @commands.bot_has_permissions(manage_webhooks=True, embed_links=True)
    async def sendhookjson(self, ctx, webhook_url_or_alias: str, *, webhook_json: str):
        """Send a message through a webhook, using JSON (⚠️ Sensitive info)

        Supports embeds.

        Use https://discohook.org to design your message, then click "JSON Data Editor" at the bottom, "Copy to Clipboard", and send here.

        -
        
        ⚠️ Webhook URLs are sensitive information. **Anyone can use them to send messages into your chat!** Please only run these commands in private guild channels.
        
        Once the bot receives your command, it will be deleted, for security purposes.
        
        For bot setup details, see **`[p]help Sendhook`**
        """
        await friendlyReact(ctx, "⏳", "Loading ⏳")

        # Check if it is an alias
        try:
            toWebhook = await validateWebhookInput(self, ctx, webhook_url_or_alias)
        except commands.UserInputError as err:
            return await ctx.send(err)

        # Try to parse JSON
        try:
            contentJson = json.loads(webhook_json)
        except json.JSONDecodeError as err:
            return await ctx.send("Error: JSON Input - "+str(err))
        except Exception as err:
            logger.error(err, exc_info=True)
            return await ctx.send("Error: "+str(err))

        # Send webhook
        try:
            await sendhookEngine(toWebhook, content=contentJson.get("content", None), embeds=contentJson.get("embeds", None))
        except ValueError as err:
            return await ctx.send("Error: "+str(err))
        except Exception as err:
            logger.error(err, exc_info=True)
            return await ctx.send("Oops, an error occurred :'( Please see bot logs for details...")
        else:
            # Success
            await friendlyReact(ctx, "✅", "Done ✅")


    @commands.hybrid_command()
    @commands.has_permissions(manage_messages=True, manage_webhooks=True)
    @commands.bot_has_permissions(manage_webhooks=True, embed_links=True)
    async def edithook(self, ctx, webhook_url_or_alias: str, message_id: str, *, webhook_text: str):
        """Edit a message sent by a webhook (⚠️ Sensitive info)

        You can set up aliases to mask the webhook URL, and make sending messages more convenient. For bot setup details, see **`[p]help Sendhook`**

        **Required user permissions:** Manage Messages, Manage Webhooks.

        -
        
        ⚠️ Webhook URLs are sensitive information. **Anyone can use them to send messages into your chat!** Please only run these commands in private guild channels.
        
        Once the bot receives your command, it will be deleted, for security purposes.
        """
        await friendlyReact(ctx, "⏳", "Loading ⏳")

        # Formatting the message_id
        if "/" in message_id:
            try:
                message_id = int(message_id.split('/')[-1])
            except Exception:
                return await ctx.send("Error: Not a valid Discord message link.")
        else:
            try:
                message_id = int(message_id)
            except Exception:
                return await ctx.send("Error: Message ID should be a string of numbers.")

        # Check if it is an alias
        try:
            toWebhook = await validateWebhookInput(self, ctx, webhook_url_or_alias)
        except commands.UserInputError as err:
            return await ctx.send(err)

        # Send webhook
        try:
            await edithookEngine(toWebhook=toWebhook, messageIdToEdit=message_id, content=webhook_text)
        except ValueError as err:
            return await ctx.send("Error: "+str(err))
        except Exception as err:
            logger.error(err, exc_info=True)
            return await ctx.send("Oops, an error occurred :'( Please see bot logs for details...")
        else:
            # Success
            await friendlyReact(ctx, "✅", "Done ✅")


    @commands.hybrid_command()
    @commands.has_permissions(manage_messages=True, manage_webhooks=True)
    @commands.bot_has_permissions(manage_webhooks=True, embed_links=True)
    async def edithookjson(self, ctx, webhook_url_or_alias: str, message_id: str, *, webhook_json: str):
        """Edit a message sent by a webhook, using JSON (⚠️ Sensitive info)

        Supports embeds.

        Use https://discohook.org to design your message, then click "JSON Data Editor" at the bottom, "Copy to Clipboard", and send here.

        -
        
        ⚠️ Webhook URLs are sensitive information. **Anyone can use them to send messages into your chat!** Please only run these commands in private guild channels.
        
        Once the bot receives your command, it will be deleted, for security purposes.
        """
        await friendlyReact(ctx, "⏳", "Loading ⏳")

        # Formatting the message_id
        if "/" in message_id:
            try:
                message_id = int(message_id.split('/')[-1])
            except Exception:
                return await ctx.send("Error: Not a valid Discord message link.")
        else:
            try:
                message_id = int(message_id)
            except Exception:
                return await ctx.send("Error: Message ID should be a string of numbers.")

        # Check if it is an alias
        try:
            toWebhook = await validateWebhookInput(self, ctx, webhook_url_or_alias)
        except commands.UserInputError as err:
            return await ctx.send(err)

        # Try to parse JSON
        try:
            contentJson = json.loads(webhook_json)
        except json.JSONDecodeError as err:
            return await ctx.send("Error: JSON Input - "+str(err))
        except Exception as err:
            logger.error(err, exc_info=True)
            return await ctx.send("Error: "+str(err))

        # Send webhook
        try:
            await edithookEngine(toWebhook=toWebhook, messageIdToEdit=message_id, content=contentJson.get("content", None), embeds=contentJson.get("embeds", None))
        except ValueError as err:
            return await ctx.send("Error: "+str(err))
        except Exception as err:
            logger.error(err, exc_info=True)
            return await ctx.send("Oops, an error occurred :'( Please see bot logs for details...")
        else:
            # Success
            await friendlyReact(ctx, "✅", "Done ✅")


    @commands.guild_only()
    @commands.hybrid_group(name="sendhooktools")
    @commands.has_permissions(manage_webhooks=True)
    @commands.bot_has_permissions(manage_webhooks=True)
    async def sendhooktools(self, ctx: commands.Context):
        """Tools for working with webhooks

        Quick tools to configure webhooks on the go

        Many commands are now available directly in Discord Mobile:
        See `#channel settings` > `Integrations` > `Webhooks`

        -

        ⚠️ Webhook URLs are sensitive information. **Anyone can use them to send messages into your chat!** Please only run these commands in private guild channels.
        """
        if not ctx.invoked_subcommand:
            pass

    @sendhooktools.command()
    @commands.has_permissions(manage_webhooks=True)
    @commands.bot_has_permissions(manage_webhooks=True, embed_links=True)
    async def newhook(self, ctx, webhook_name: str, webhook_image: str=None, channel: discord.TextChannel=None):
        """Create a webhook in a channel (⚠️ Sensitive info)
        
        - webhook_name: Name of webhook
        - webhook_image *(optional)*: URL of image to fetch, for webhook avatar (profile pic) - upload to a Discord channel and copy image URL
        - channel *(optional)*: Channel to create webhook in (default: current channel)

        ⚠️ Webhook URLs are sensitive information. **Anyone can use them to send messages into your chat!** Please only run these commands in private guild channels.
        """
        if channel == None:
            channel = ctx.message.channel
        # Loading
        await friendlyReact(ctx, "⏳", "Loading ⏳")

        wimgdata = None
        if webhook_image:
            async with aiohttp.ClientSession() as session:
                async with session.get(webhook_image) as resp:
                    if resp.status != 200:
                        return await channel.send('Could not fetch image... Server error.')
                    try:
                        wimgdata = await resp.read()
                    except Exception as err:
                        logger.error(err)
                        return await channel.send('Could not fetch image... Response error.')

        try:
            thenewhook = await channel.create_webhook(name=webhook_name, avatar=wimgdata)
        except Exception as err:
            logger.error(err)
            await ctx.send("Could not create webhook. Please see bot logs for details...")
        else:
            # Success
            await friendlyReact(ctx, "✅", "Done ✅")
            await ctx.send(str(channel.mention)+" "+str(thenewhook.name)+" - ||"+str(thenewhook.url)+"||")

    @sendhooktools.command()
    @commands.has_permissions(manage_guild=True, manage_webhooks=True)
    @commands.bot_has_permissions(manage_webhooks=True)
    async def listhooks(self, ctx, channel: discord.TextChannel):
        """List the webhooks in a channel (⚠️ Sensitive info)

        ⚠️ Webhook URLs are sensitive information. **Anyone can use them to send messages into your chat!** Please only run these commands in private guild channels.
        """

        # 2025-03-14: Removing default channel, to force the help popup by default.
        #     Not leaking webhook URLs by default

        # if channel == None:
        #     channel = ctx.message.channel

        a = await channel.webhooks()

        # Exit if empty
        if len(a) <= 0:
            return await ctx.send("No webhooks found in this channel.")

        returntext = ""

        for b in a:
            name = str(b.name)
            url = str(b.url)
            returntext += "- "+name+" - ||"+url+"||\n"

        try:
            await ctx.send(returntext[:1999])
        except discord.HTTPException as err:
            return await ctx.send(err)
