from redbot.core import Config, commands, checks
# from array import *
import discord
from discord import Webhook, SyncWebhook
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

    # This cog does not store any End User Data
    async def red_get_data_for_user(self, *, user_id: int):
        return {}
    async def red_delete_data_for_user(self, *, requester, user_id: int) -> None:
        pass


    # Utility Commands

    async def sendhookEngine(self, toWebhook, messageObj, webhookText=None, webhookUser=None, webhookAvatar=None):
        # Start webhook session
        webhook = SyncWebhook.from_url(toWebhook)

        # Check for attachments
        if messageObj.attachments:
            # Send message first if there is a message
            if webhookText is not None:
                webhook.send(
                    webhookText,
                    username=webhookUser,
                    avatar_url=webhookAvatar
                )
            # Then send each attachment in separate messages
            for msgAttach in messageObj.attachments:
                try:
                    webhook.send(
                        username=webhookUser,
                        avatar_url=webhookAvatar,
                        file=await msgAttach.to_file()
                    )
                except:
                    # Couldn't send, retry sending file as url only
                    webhook.send(
                        "File: "+str(msgAttach.url), 
                        username=webhookUser,
                        avatar_url=webhookAvatar
                    )
        else:
            webhook.send(
                webhookText,
                username=webhookUser,
                avatar_url=webhookAvatar
            )


    # Bot Commands

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
    async def sendhook(self, ctx, webhookUrl, *, webhookText=None):
        """Send a webhook
        
        webhookUrl can be an alias"""

        message = ctx.message

        # Check if webhookUrl is an alias
        webhookAlias = await self.config.guild(ctx.guild).webhookAlias()
        if webhookUrl in webhookAlias:
            toWebhook = webhookAlias[webhookUrl]
        else:
            toWebhook = webhookUrl

        # Send webhook
        try:
            await self.sendhookEngine(toWebhook, message, webhookText)
        except:
            await ctx.send("Oops, an error occurred :'(")
        else:
            await ctx.message.add_reaction("✅")


    @commands.command()
    @checks.mod()
    async def sendhookself(self, ctx, webhookUrl, *, webhookText=None):
        """Send a webhook as yourself
        
        webhookUrl can be an alias"""

        message = ctx.message

        # Check if webhookUrl is an alias
        webhookAlias = await self.config.guild(ctx.guild).webhookAlias()
        if webhookUrl in webhookAlias:
            toWebhook = webhookAlias[webhookUrl]
        else:
            toWebhook = webhookUrl

        # Send webhook
        try:
            await self.sendhookEngine(toWebhook, message, webhookText, message.author.display_name, message.author.display_avatar.url)
        except:
            await ctx.send("Oops, an error occurred :'(")
        else:
            await ctx.message.add_reaction("✅")


    @commands.command()
    @checks.mod()
    async def edithook(self, ctx, webhookUrl, messageId, *, webhookText):
        """Edit a message sent by a webhook
        
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
        await ctx.send(str(channel.mention)+" "+str(channel.id))
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
                    await ctx.send(str(thenewhook.name)+" "+str(thenewhook.url))

    
    @commands.command()
    @checks.mod()
    async def listhooks(self, ctx, channel: discord.TextChannel=None):
        """List the webhooks in a channel"""
        if channel == None:
            channel = ctx.message.channel

        a = await channel.webhooks()
        returntext = ""

        if len(a) > 1:
            for b in a:
                name = str(b.name)
                url = str(b.url)
                returntext += name+"\n"+url+"\n\n"
        else:
            name = str(b.name)
            url = str(b.url)
            returntext += name+" "+url+"\n"

        await ctx.send(returntext)
