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
    @commands.group()
    @commands.has_permissions(manage_guild=True, manage_webhooks=True)
    @commands.bot_has_permissions(manage_webhooks=True)
    async def aliashook(self, ctx: commands.Context):
        """Configure aliases for webhooks in your server

        -

        ⚠️ Webhook URLs are sensitive information. **Anyone can use them to send messages into your chat!** Please only run these commands in private guild channels.
        """
        if not ctx.invoked_subcommand:
            pass

    @aliashook.command(name="add")
    @commands.has_permissions(manage_guild=True, manage_webhooks=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def ahadd(self, ctx, alias: str, webhookUrl: str):
        """Add an alias for a webhook (⚠️ Sensitive info)
        
        To create an alias, you need a webhook URL.

        Create a webhook in Discord settings, or use **`[p]sendhooktools newhook`**

        ⚠️ Webhook URLs are sensitive information. **Anyone can use them to send messages into your chat!** Please only run these commands in private guild channels. Once the bot receives your command, it will be deleted, for security purposes.
        """

        # Immediately delete the command message, to hide webhook URL
        await ctx.message.delete()
        creating = await ctx.send("Creating ⏳")

        webhookAlias = await self.config.guild(ctx.guild).webhookAlias()
        webhookAlias[alias] = webhookUrl
        await self.config.guild(ctx.guild).webhookAlias.set(webhookAlias)
        # Try to clear the loading prompt, but not important even if it fails
        try:
            await creating.delete()
        except discord.NotFound:
            pass
        except Exception as err:
            logger.error(err)
            pass
        # Success
        try:
            await creating.edit(content="Webhook alias added successfully. ✅")
        except Exception:
            await ctx.send("Webhook alias added successfully. ✅")

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
            if ctx.channel.permissions_for(ctx.guild.me).add_reactions:
                await ctx.message.add_reaction("✅")
            else:
                await ctx.send("Done ✅")
        except KeyError:
            pass

    @aliashook.command(name="list")
    @commands.has_permissions(manage_guild=True, manage_webhooks=True)
    async def ahlist(self, ctx, safeMode: bool=True):
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
            if safeMode == True:
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


    @commands.command()
    @commands.has_permissions(manage_webhooks=True)
    @commands.bot_has_permissions(manage_webhooks=True, embed_links=True)
    async def sendhook(self, ctx, webhookUrl_or_alias: str, *, webhookText: str=None):
        """Send a message through a webhook (⚠️ Sensitive info)
        
        You can set up aliases to mask the webhook URL, and make sending messages more convenient. For bot setup details, see **`[p]help Sendhook`**

        **Required user permissions:** Manage Webhooks.

        -
        
        ⚠️ Webhook URLs are sensitive information. **Anyone can use them to send messages into your chat!** Please only run these commands in private guild channels.
        
        Once the bot receives your command, it will be deleted, for security purposes.
        """
        creating = await ctx.send("Sending ⏳")

        # Check if it is an alias
        try:
            toWebhook = await validateWebhookInput(self, ctx, webhookUrl_or_alias)
        except commands.UserInputError as err:
            return await ctx.send(err)

        # Send webhook
        try:
            await sendhookEngine(toWebhook, content=webhookText, attachments=ctx.message.attachments)
        except ValueError as err:
            try:
                await creating.edit(content="Error: "+str(err))
            except Exception:
                await ctx.send("Error: "+str(err))
        except Exception as err:
            logger.error(err, exc_info=True)
            err_text = "Oops, an error occurred :'( Please see bot logs for details..."
            try:
                await creating.edit(content=err_text)
            except Exception:
                await ctx.send(err_text)
        else:
            # Success
            try:
                await creating.edit(content="Sent successfully. ✅")
                # Delete the command message, to hide webhook URL, after all attachments uploaded, silently fail OK
                await ctx.message.delete()
            except Exception:
                await ctx.send("Sent successfully. ✅")


    @commands.command()
    @commands.has_permissions(manage_webhooks=True)
    @commands.bot_has_permissions(manage_webhooks=True, embed_links=True)
    async def sendhookself(self, ctx, webhookUrl_or_alias: str, *, webhookText: str=None):
        """Send a webhook as yourself (⚠️ Sensitive info)

        You can set up aliases to mask the webhook URL, and make sending messages more convenient. For bot setup details, see **`[p]help Sendhook`**

        **Required user permissions:** Manage Webhooks.

        -
        
        ⚠️ Webhook URLs are sensitive information. **Anyone can use them to send messages into your chat!** Please only run these commands in private guild channels.
        
        Once the bot receives your command, it will be deleted, for security purposes.
        """
        creating = await ctx.send("Sending ⏳")

        # Check if it is an alias
        try:
            toWebhook = await validateWebhookInput(self, ctx, webhookUrl_or_alias)
        except commands.UserInputError as err:
            return await ctx.send(err)

        # Send webhook
        try:
            await sendhookEngine(toWebhook, content=webhookText, attachments=ctx.message.attachments, webhookUser=ctx.message.author.display_name, webhookAvatar=ctx.message.author.display_avatar.url)
        except ValueError as err:
            try:
                await creating.edit(content="Error: "+str(err))
            except Exception:
                await ctx.send("Error: "+str(err))
        except Exception as err:
            logger.error(err, exc_info=True)
            err_text = "Oops, an error occurred :'( Please see bot logs for details..."
            try:
                await creating.edit(content=err_text)
            except Exception:
                await ctx.send(err_text)
        else:
            # Success
            try:
                await creating.edit(content="Sent successfully. ✅")
                # Delete the command message, to hide webhook URL, after all attachments uploaded, silently fail OK
                await ctx.message.delete()
            except Exception:
                await ctx.send("Sent successfully. ✅")


    @commands.command()
    @commands.has_permissions(manage_webhooks=True)
    @commands.bot_has_permissions(manage_webhooks=True, embed_links=True)
    async def sendhookjson(self, ctx, webhookUrl_or_alias: str, *, webhookJson: str):
        """Send a message through a webhook, using JSON (⚠️ Sensitive info)

        Supports embeds.

        Use https://discohook.org to design your message, then click "JSON Data Editor" at the bottom, "Copy to Clipboard", and send here.

        -
        
        ⚠️ Webhook URLs are sensitive information. **Anyone can use them to send messages into your chat!** Please only run these commands in private guild channels.
        
        Once the bot receives your command, it will be deleted, for security purposes.
        
        For bot setup details, see **`[p]help Sendhook`**
        """
        creating = await ctx.send("Sending ⏳")

        # Check if it is an alias
        try:
            toWebhook = await validateWebhookInput(self, ctx, webhookUrl_or_alias)
        except commands.UserInputError as err:
            return await ctx.send(err)

        # Try to parse JSON
        try:
            contentJson = json.loads(webhookJson)
        except Exception as err:
            logger.error(err, exc_info=True)
            return await ctx.send("Error: "+str(err))

        # Send webhook
        try:
            await sendhookEngine(toWebhook, content=contentJson.get("content", None), embeds=contentJson.get("embeds", None))
        except ValueError as err:
            try:
                await creating.edit(content="Error: "+str(err))
            except Exception:
                await ctx.send("Error: "+str(err))
        except Exception as err:
            logger.error(err, exc_info=True)
            err_text = "Oops, an error occurred :'( Please see bot logs for details..."
            try:
                await creating.edit(content=err_text)
            except Exception:
                await ctx.send(err_text)
        else:
            # Success
            try:
                await creating.edit(content="Sent successfully. ✅")
                # Delete the command message, to hide webhook URL, after all attachments uploaded, silently fail OK
                await ctx.message.delete()
            except Exception:
                await ctx.send("Sent successfully. ✅")


    @commands.command()
    @commands.has_permissions(manage_messages=True, manage_webhooks=True)
    @commands.bot_has_permissions(manage_webhooks=True, embed_links=True)
    async def edithook(self, ctx, webhookUrl_or_alias: str, messageId: str, *, webhookText: str):
        """Edit a message sent by a webhook (⚠️ Sensitive info)

        You can set up aliases to mask the webhook URL, and make sending messages more convenient. For bot setup details, see **`[p]help Sendhook`**

        **Required user permissions:** Manage Messages, Manage Webhooks.

        -
        
        ⚠️ Webhook URLs are sensitive information. **Anyone can use them to send messages into your chat!** Please only run these commands in private guild channels.
        
        Once the bot receives your command, it will be deleted, for security purposes.
        """
        creating = await ctx.send("Sending ⏳")

        # Formatting the messageId
        if "/" in messageId:
            try:
                messageId = int(messageId.split('/')[-1])
            except Exception:
                return await ctx.send("Error: Not a valid Discord message link.")
        else:
            try:
                messageId = int(messageId)
            except Exception:
                return await ctx.send("Error: Message ID should be a string of numbers.")

        # Check if it is an alias
        try:
            toWebhook = await validateWebhookInput(self, ctx, webhookUrl_or_alias)
        except commands.UserInputError as err:
            return await ctx.send(err)

        # Send webhook
        try:
            await edithookEngine(toWebhook=toWebhook, messageIdToEdit=messageId, content=webhookText)
        except ValueError as err:
            try:
                await creating.edit(content="Error: "+str(err))
            except Exception:
                await ctx.send("Error: "+str(err))
        except Exception as err:
            logger.error(err, exc_info=True)
            err_text = "Oops, an error occurred :'( Please see bot logs for details..."
            try:
                await creating.edit(content=err_text)
            except Exception:
                await ctx.send(err_text)
        else:
            # Success
            try:
                await creating.edit(content="Sent successfully. ✅")
                # Delete the command message, to hide webhook URL, after all attachments uploaded, silently fail OK
                await ctx.message.delete()
            except Exception:
                await ctx.send("Sent successfully. ✅")


    @commands.command()
    @commands.has_permissions(manage_messages=True, manage_webhooks=True)
    @commands.bot_has_permissions(manage_webhooks=True, embed_links=True)
    async def edithookjson(self, ctx, webhookUrl_or_alias: str, messageId: str, *, webhookJson: str):
        """Edit a message sent by a webhook, using JSON (⚠️ Sensitive info)

        Supports embeds.

        Use https://discohook.org to design your message, then click "JSON Data Editor" at the bottom, "Copy to Clipboard", and send here.

        -
        
        ⚠️ Webhook URLs are sensitive information. **Anyone can use them to send messages into your chat!** Please only run these commands in private guild channels.
        
        Once the bot receives your command, it will be deleted, for security purposes.
        """
        creating = await ctx.send("Sending ⏳")

        # Formatting the messageId
        if "/" in messageId:
            try:
                messageId = int(messageId.split('/')[-1])
            except Exception:
                return await ctx.send("Error: Not a valid Discord message link.")
        else:
            try:
                messageId = int(messageId)
            except Exception:
                return await ctx.send("Error: Message ID should be a string of numbers.")

        # Check if it is an alias
        try:
            toWebhook = await validateWebhookInput(self, ctx, webhookUrl_or_alias)
        except commands.UserInputError as err:
            return await ctx.send(err)

        # Try to parse JSON
        try:
            contentJson = json.loads(webhookJson)
        except Exception as err:
            logger.error(err, exc_info=True)
            return await ctx.send("Error: "+str(err))

        # Send webhook
        try:
            await edithookEngine(toWebhook=toWebhook, messageIdToEdit=messageId, content=contentJson.get("content", None), embeds=contentJson.get("embeds", None))
        except ValueError as err:
            try:
                await creating.edit(content="Error: "+str(err))
            except Exception:
                await ctx.send("Error: "+str(err))
        except Exception as err:
            logger.error(err, exc_info=True)
            err_text = "Oops, an error occurred :'( Please see bot logs for details..."
            try:
                await creating.edit(content=err_text)
            except Exception:
                await ctx.send(err_text)
        else:
            # Success
            try:
                await creating.edit(content="Sent successfully. ✅")
                # Delete the command message, to hide webhook URL, after all attachments uploaded, silently fail OK
                await ctx.message.delete()
            except Exception:
                await ctx.send("Sent successfully. ✅")


    @commands.guild_only()
    @commands.group()
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
    async def newhook(self, ctx, webhookName: str, webhookImage: str=None, channel: discord.TextChannel=None):
        """Create a webhook in a channel (⚠️ Sensitive info)
        
        - webhookName: Name of webhook
        - webhookImage *(optional)*: URL of image to fetch, for webhook avatar (profile pic)
        - channel *(optional)*: Channel to create webhook in (default: current channel)

        ⚠️ Webhook URLs are sensitive information. **Anyone can use them to send messages into your chat!** Please only run these commands in private guild channels.
        """
        if channel == None:
            channel = ctx.message.channel
        # Loading
        if ctx.channel.permissions_for(ctx.guild.me).add_reactions:
            await ctx.message.add_reaction("⏳")
        else:
            await ctx.send("Loading ⏳")
        await ctx.send(str(channel.mention)+" "+str(channel.id))

        wimgdata = None
        if webhookImage:
            async with aiohttp.ClientSession() as session:
                async with session.get(webhookImage) as resp:
                    if resp.status != 200:
                        return await channel.send('Could not fetch image... Server error.')
                    try:
                        wimgdata = await resp.read()
                    except Exception as err:
                        logger.error(err)
                        return await channel.send('Could not fetch image... Response error.')

        try:
            thenewhook = await channel.create_webhook(name=webhookName, avatar=wimgdata)
        except Exception as err:
            logger.error(err)
            await ctx.send("Could not create webhook. Please see bot logs for details...")
        else:
            # Success
            if ctx.channel.permissions_for(ctx.guild.me).add_reactions:
                await ctx.message.add_reaction("✅")
            else:
                await ctx.send("Done ✅")
            await ctx.send(str(thenewhook.name)+" - ||"+str(thenewhook.url)+"||")

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
