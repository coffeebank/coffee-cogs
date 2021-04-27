from redbot.core import Config, commands, checks
# from array import *
from dhooks import Webhook, Embed
import discord
from discord import Webhook, AsyncWebhookAdapter
import aiohttp
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
    @checks.mod()
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
    @checks.mod()
    async def sendhookself(self, ctx, webhookUrl, *, webhookText):
        """Send a webhook as yourself
        
        webhookUrl can be an alias"""

        message = ctx.message

        # Check if webhookUrl is an alias
        webhookAlias = await self.config.guild(ctx.guild).webhookAlias()
        if webhookUrl in webhookAlias:
            toWebhook = webhookAlias[webhookUrl]
        else:
            toWebhook = webhookUrl

        # Start webhook session
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(toWebhook, adapter=AsyncWebhookAdapter(session))

            # Check for attachments
            if message.attachments:
                # Send message first if there is a message
                if webhookText:
                    await webhook.send(
                        webhookText,
                        username=message.author.display_name,
                        avatar_url=message.author.avatar_url
                    )
                # Then send each attachment in separate messages
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
            else:
                await webhook.send(
                    webhookText,
                    username=message.author.display_name,
                    avatar_url=message.author.avatar_url
                )

        await ctx.message.add_reaction("✅")


    @commands.command()
    @checks.mod()
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


    @commands.command()
    @checks.mod()
    async def newhook(self, ctx, webhookName, webhookImage, channel: discord.TextChannel=None):
        """Create a webhook"""
        if channel == None:
            channel = ctx.message.channel
        await ctx.message.add_reaction("⏳")
        await ctx.send(channel.id)
        async with aiohttp.ClientSession() as session:
            async with session.get(webhookImage) as resp:
                if resp.status != 200:
                    return await channel.send('Could not download file...')
                wimgdata = await resp.read()
                try:
                    thenewhook = await channel.create_webhook(name=webhookName, avatar=wimgdata)
                except Exception as e:
                    await ctx.send("Could not create webhook. Do I have permissions to create webhooks?\n"+str(e)+"\n"+str(wimgdata))
                else:
                    await ctx.message.add_reaction("✅")
                    await ctx.send(thenewhook)

    
    @commands.command()
    @checks.mod()
    async def listhooks(self, ctx, channel: discord.TextChannel=None):
        """List the webhooks in a channel"""
        if channel == None:
            channel = ctx.message.channel
        try:
            await ctx.send(str([[a.name, a.url, a.token] for a in channel.webhooks()]))
        except:
            a = await channel.webhooks()
            await ctx.send([a.name, a.url, a.token])
