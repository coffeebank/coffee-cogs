from redbot.core import Config, commands, checks
# from array import *
from dhooks import Webhook, Embed
import asyncio
import requests
import json

class Sendhook(commands.Cog):
    """Send webhooks easily..."""

    def __init__(self):
        self.config = Config.get_conf(self, identifier=806715409318936616)
        default_guild = {
            "webhookAlias": {}
        }
        self.config.register_guild(**default_guild)


    @commands.guild_only()
    @commands.group()
    @checks.mod()
    async def aliashook(self, ctx: commands.Context):
        """Configure aliases for webhooks in your server"""
        if not ctx.invoked_subcommand:
            pass

    @aliashook.command(name="add")
    async def ahadd(self, ctx, alias, webhookUrl):
        """Add an alias for a webhook"""
        webhookAlias = await self.config.guild(ctx.guild).webhookAlias()
        webhookAlias[alias] = webhookUrl
        await self.config.guild(ctx.guild).webhookAlias.set(webhookAlias)
        # Try adding react, if no perms then send normal message
        try:
            await ctx.message.add_reaction("✅")
        except:
            await ctx.send("Webhook alias added ✅")

    @aliashook.command(name="remove")
    async def ahremove(self, ctx, alias):
        """Remove an alias for a webhook"""
        webhookAlias = await self.config.guild(ctx.guild).webhookAlias()
        try:
            # Try to set alias to empty, before removing
            webhookAlias[alias] = ""
            del webhookAlias[alias]
            await self.config.guild(ctx.guild).webhookAlias.set(webhookAlias)
            # Try adding react, if no perms then send normal message
            try:
                await ctx.message.add_reaction("✅")
            except:
                await ctx.send("Webhook alias removed ✅")
        except KeyError:
            pass

    @aliashook.command(name="list")
    async def ahlist(self, ctx):
        """List all aliases for webhooks"""
        webhookAlias = await self.config.guild(ctx.guild).webhookAlias()
        webhookData = json.dumps(webhookAlias, sort_keys=True, indent=2, separators=(',', ': '))
        await ctx.send("```json\n"+webhookData+"```")

    @aliashook.command(name="show")
    async def ahshow(self, ctx, alias):
        """Show the saved webhook url for an alias"""
        webhookAlias = await self.config.guild(ctx.guild).webhookAlias()
        webhookData = webhookAlias[alias]
        await ctx.send("```"+webhookData+"```")


    # @commands.bot_has_permissions(embed_links=True, add_reactions=True)

    @commands.command()
    async def sendhook(self, ctx, webhookUrl, *, webhookText):
        """Send a webhook
        
        webhookUrl can be an alias"""

        # Check if webhookUrl is an alias
        webhookAlias = await self.config.guild(ctx.guild).webhookAlias()
        if webhookUrl in webhookAlias:
            hook = Webhook(webhookAlias[webhookUrl])
        else:
            hook = Webhook(webhookUrl)
        
        try:
            hook.send(webhookText)
            # TODO: Make it return message ID after send
            # hooktosend = hook.send(webhookText)
            # await ctx.send(f"Message ID: {hooktosend}")
        except:
            await ctx.send("Oh no! Webhook couldn't be sent :(")
        else:
            # Try adding react, if no perms then send normal message
            try:
                await ctx.message.add_reaction("✅")
            except:
                await ctx.send("Webhook sent ✅")


    @commands.command()
    async def edithook(self, ctx, webhookUrl, messageId, *, webhookText):
        """Edit a webhook
        
        webhookUrl can be an alias"""

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
        else:
            # Try adding react, if no perms then send normal message
            try:
                await ctx.message.add_reaction("✅")
            except:
                await ctx.send("Webhook updated ✅")
