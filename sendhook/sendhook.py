# from redbot.core import Config
from redbot.core import Config, commands, checks
from array import *
from dhooks import Webhook, Embed
import asyncio
import requests
import json

class sendhook(commands.Cog):
    """Send webhooks easily..."""

    def __init__(self):
        self.config = Config.get_conf(self, identifier=806715409318936616)
        default_guild = {
            "webhookAlias": {}
        }
        self.config.register_guild(**default_guild)


    @commands.command()
    async def aliashook(self, ctx, subcommand, alias_name="", webhookUrl=""):
        """Aliases for your webhooks
        
        [p]aliashook list
        [p]aliashook add <alias_name> <webhookUrl>
        [p]aliashook remove <alias_name>
        """
        webhookAlias = await self.config.guild(ctx.guild).webhookAlias()
        if subcommand == "add":
            webhookAlias[alias_name] = webhookUrl
            await self.config.guild(ctx.guild).webhookAlias.set(webhookAlias)
            # Try adding react, if no perms then send normal message
            try:
                await ctx.message.add_reaction("✅")
            except:
                await ctx.send("Webhook alias added ✅")
        elif subcommand == "remove":
            try:
                # Try to set alias to empty, before removing
                webhookAlias[alias_name] = webhookUrl
                del webhookAlias[alias_name]
                await self.config.guild(ctx.guild).webhookAlias.set(webhookAlias)
                # Try adding react, if no perms then send normal message
                try:
                    await ctx.message.add_reaction("✅")
                except:
                    await ctx.send("Webhook alias removed ✅")
            except KeyError:
                pass
        else:
            await ctx.send(webhookAlias)


    # @commands.bot_has_permissions(embed_links=True, add_reactions=True)

    @commands.command()
    async def sendhook(self, ctx, webhookUrl, *, webhookText):
        """Send a webhook"""

        # Check if webhookUrl is an alias
        webhookAlias = await self.config.guild(ctx.guild).webhookAlias()
        if webhookUrl in webhookAlias:
            hook = Webhook(webhookAlias[webhookUrl])
        else:
            hook = Webhook(webhookUrl)
        
        try:
            hook.send(webhookText)
        except:
            await ctx.send("Oh no! Webhook couldn't be sent :(")
        finally:
            # Try adding react, if no perms then send normal message
            try:
                await ctx.message.add_reaction("✅")
            except:
                await ctx.send("Webhook sent ✅")


    @commands.command()
    async def edithook(self, ctx, webhookUrl, messageId, *, webhookText):
        """Edit a webhook"""

        # Formatting the messageId
        forgotMsgLink = "Oh no! Did you remember to include the message link to the message you want to edit?"
        if isinstance(messageId, str):
            try:
                messageId = int(messageId.split('/')[-1])
            except:
                await ctx.send(forgotMsgLink)
        elif isinstance(messageId, int):
            pass
        else:
            await ctx.send(forgotMsgLink)

        # Check if webhookUrl is an alias
        webhookAlias = await self.config.guild(ctx.guild).webhookAlias()
        if webhookUrl in webhookAlias:
            url = str(webhookAlias[webhookUrl]) + "/messages/" + str(messageId)
        else:
            url = str(webhookUrl) + "/messages/" + str(messageId)

        # Formatting the payload
        head = {"Content-Type":"application/json"}
        payload = {"content": str(webhookText) }

        try:
            requests.patch(url, json=payload, headers=head)
        except:
            await ctx.send("Oh no! Webhook couldn't be sent :(")
        finally:
            # Try adding react, if no perms then send normal message
            try:
                await ctx.message.add_reaction("✅")
            except:
                await ctx.send("Webhook updated ✅")
