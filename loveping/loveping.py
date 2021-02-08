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
        await ctx.send("Cleaned the love cannon. Ready to be reloaded using `[p]setlove` again :)")
    
    @commands.command()
    async def whatislove(self, ctx):
        whookData = await self.config.guild(ctx.guild).loveCannon()
        if whookData:
            await ctx.send(whookData)
        else:
            await ctx.send("The love cannon is empty. Ready to be reloaded using `[p]setlove` again :)")

    @commands.command()
    async def lovecannon(self, ctx, usermention):
        """Ping someone to send them messages of love... [cannon edition]
        
        command: [p]lovecannon @user
        """

        whookData = await self.config.guild(ctx.guild).loveCannon()
        if whookData != "":
            hook = Webhook.Async(whookData)

            # ping torrent
            # removed multi-webhook support, maybe another day :')
            x = 0
            while x < 15:
                time.sleep(0.6)
                await hook.send("Hi i love you "+usermention+" :)")
                x += 1
            await hook.close()

        else:
            await ctx.send("I love you too <3 Add a webhook url using `[p]setlove` :)")


    @commands.command()
    async def loverain(self, ctx, usermention):
        """Ping someone to send them messages of love... [rain edition]
        
        command: [p]loverain @user
        """

        whookData = await self.config.guild(ctx.guild).loveCannon()
        if whookData != "":
            hook = Webhook.Async(whookData)

            # ping rain
            for rainCount in range(14):
                print("pingRain #", rainCount)
                await hook.send("Please give me some love "+usermention+" :'(")
                await asyncio.sleep(random.randint(10, 30))
            await hook.close()

        else:
            await ctx.send("I love you too <3 Add a webhook url using `[p]setlove` :)")

    
    @commands.command()
    async def loveping(self, ctx, usermention):
        """Ping someone to send them messages of love...
        
        command: [p]loveping @user
        """

        loveGifs = [
            "https://tenor.com/view/a-whisker-away-hug-love-anime-embrace-gif-17694740",
            "https://tenor.com/view/anime-couples-cuddles-nuzzles-snuggles-gif-15069987",
            "https://tenor.com/view/tonikaku-kawaii-tonikaku-kawaii-tonikawa-over-the-moon-for-you-gif-18959319",
            "https://tenor.com/view/horimiya-izumi-miyamura-hori-kyoko-couple-hug-gif-14539121",
            "https://tenor.com/view/anime-cute-in-love-happy-gif-4394528"
        ]

        whookData = await self.config.guild(ctx.guild).loveCannon()
        if whookData != "":
            x = 0
            hook = Webhook.Async(whookData)
            while x < 8:
                time.sleep(0.3)
                await hook.send("Hi i love you "+usermention+" :)")
                time.sleep(0.1)
                await hook.send(random.choice(loveGifs))
                x += 1
            await hook.close()
        else:
            await ctx.send("I love you too <3 Add a webhook url using `[p]setlove` :)")

