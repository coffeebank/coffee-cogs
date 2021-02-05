# from redbot.core import Config
from redbot.core import Config, commands, checks
from array import *
from dhooks import Webhook, Embed
import asyncio
import aiohttp
import discord
import time
import random

class loveping(commands.Cog):
    """Ping someone to send them messages of love :)"""

    def __init__(self):
        self.config = Config.get_conf(self, identifier=806715409318936616)
        default_guild = {
            "loveCannon": ""
        }
        self.config.register_guild(**default_guild)

    @commands.command()
    @checks.admin_or_permissions(manage_guild=True)
    async def setlove(self, ctx, message):
        await self.config.guild(ctx.guild).loveCannon.set(message)
        await ctx.send("Reloaded the love cannon!! :)")

    async def _add_loveCannon(self, ctx, whookUrl):
        setMoreLove = self.config.guild(ctx.guild)
        async with setMoreLove.loveCannon() as loveCannon:
            loveCannon.append(whookUrl)

    @commands.command()
    @checks.admin_or_permissions(manage_guild=True)
    async def clearlove(self, ctx):
        await self.config.guild(ctx.guild).loveCannon.set("")
        await ctx.send("Cleaned the love cannon. Ready to be reloaded using `bbsetlove` again :)")
    
    @commands.command()
    async def whatislove(self, ctx):
        whookData = await self.config.guild(ctx.guild).loveCannon()
        if whookData:
            await ctx.send(whookData)
        else:
            await ctx.send("The love cannon is empty. Ready to be reloaded using `bbsetlove` again :)")

    @commands.command()
    async def loveping(self, ctx, usermention):
        """Ping someone to send them messages of love...
        
        command: [p]loveping @user
        """

        whookData = await self.config.guild(ctx.guild).loveCannon()
        if whookData != "":

            # ping torrent
            # removed multi-webhook support, maybe another day :')
            x = 0
            while x < 15:
                hook = Webhook.Async(whookData)
                time.sleep(random.uniform(0.05, 0.15))
                await hook.send("Hi i love you "+usermention+" :)")
                x += 1

            # ping rain
            await asyncio.sleep(random.randint(3, 12))
            for rainCount in range(15):
                print("pingRain #", rainCount)
                await hook.send("I still love youuu come backk "+usermention+" :'(")
                await asyncio.sleep(random.randint(3, 20))
            await hook.close()
        else:
            await ctx.send("I love you too <3 Add some webhook urls in an array format using `bbsetlove` :)")
