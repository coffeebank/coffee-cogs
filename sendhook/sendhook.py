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
            "webhooks": ""
        }
        self.config.register_guild(**default_guild)

    '''
    @commands.command()
    @checks.admin_or_permissions(manage_guild=True)
    async def sendhook(self, ctx, message):
        """Set webhooks"""
        await self.config.guild(ctx.guild).webhooks.set(message)
        await ctx.send("")
    '''

    @commands.command()
    async def sendhook(self, ctx, webhookUrl, *, webhookText):
        """Send a webhook"""

        hook = Webhook(webhookUrl)
        hook.send(webhookText)
        await ctx.send("Sent webhook")

    @commands.command()
    async def edithook(self, ctx, webhookUrl, messageId, *, webhookText):
        """Edit a webhook"""
        head = {"Content-Type":"application/json"}
        url = webhookUrl + "/messages/" + messageId
        payload = {'content' : webhookText }

        requests.patch(url, payload, headers=head)
        await ctx.send("Updated webhook")
