# from redbot.core import Config
from redbot.core import Config, commands, checks
from array import *
from dhooks import Webhook, Embed
import asyncio
import aiohttp
import discord
import requests
import time
import random

class Loveping(commands.Cog):
    """Ping someone to send them messages of love :)"""

    def __init__(self):
        self.config = Config.get_conf(self, identifier=806715409318936616)
        default_guild = {
            "loveCannon": "",
            "loveMute": "",
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
    @checks.mod()
    async def setlovemute(self, ctx, role: discord.Role):
        """Set the lovemute role"""
        await self.config.guild(ctx.guild).loveMute.set(role.id)
        await ctx.message.add_reaction("✅")

    @commands.command()
    @commands.cooldown(rate=1, per=40, type=commands.BucketType.guild)
    async def lovecannon(self, ctx, usermention):
        """Ping someone to send them messages of love... [cannon edition]
        
        command: [p]lovecannon @user
        """
        msgid = ctx.message.id
        whookData = await self.config.guild(ctx.guild).loveCannon()
        if whookData != "":
            hook = Webhook.Async(whookData)

            # ping torrent
            for i in range(20):
                print("pingCannon #", i)
                newmsgcontent = await ctx.fetch_message(msgid)
                if usermention in newmsgcontent.content:
                    await hook.send("Hi i love you "+usermention+" :)")
                    await asyncio.sleep(0.2)
                else:
                    return await hook.send("Thanks for having fun with us "+usermention+" :')")
            await hook.close()

        else:
            await ctx.send("I love you too <3 Add a webhook url using `[p]setlove` :)")


    @commands.command()
    @commands.cooldown(rate=4, per=300, type=commands.BucketType.guild)
    async def loverain(self, ctx, usermention):
        """Ping someone to send them messages of love... [rain edition]
        
        command: [p]loverain @user
        """
        msgid = ctx.message.id
        whookData = await self.config.guild(ctx.guild).loveCannon()
        if whookData != "":
            hook = Webhook.Async(whookData)

            # ping rain
            for i in range(60):
                print("pingRain #", i)
                newmsgcontent = await ctx.fetch_message(msgid)
                if usermention in newmsgcontent.content:
                    await hook.send("Please give me some love "+usermention+" :'(")
                    await asyncio.sleep(random.randint(10, 45))
                else:
                    return await hook.send("Thanks for having fun with us "+usermention+" :')")
            await hook.close()

        else:
            await ctx.send("I love you too <3 Add a webhook url using `[p]setlove` :)")


    @commands.command()
    @checks.mod()
    @commands.cooldown(rate=4, per=300, type=commands.BucketType.guild)
    async def lovemute(self, ctx, usermention: discord.Member):
        """Wreck some havoc while muting peeps :)
        
        If you're not mod, give [p]lovecannon a try :'))"""

        # Find the role in server
        muteroledata = await self.config.guild(ctx.guild).loveMute()
        muterole = ctx.guild.get_role(muteroledata)

        # Replace all of a user's roles with just [muterole]
        try:
            await usermention.edit(roles=[muterole])
        except:
            return await ctx.send("Be sure to set the muterole first using [p]setlovemute :)")

        msgid = ctx.message.id
        whookData = await self.config.guild(ctx.guild).loveCannon()
        checklove = "love"

        if whookData != "":
            hook = Webhook.Async(whookData)

            # ping torrent
            for i in range(20):
                print("pingCannon #", i)
                newmsgcontent = await ctx.fetch_message(msgid)
                if checklove in newmsgcontent.content:
                    await hook.send("Hi i love you "+usermention.mention+" :)")
                    await asyncio.sleep(0.2)
                else:
                    return await hook.send("Thanks for having fun with us "+usermention.mention+" :')")

            # ping rain
            for ii in range(60):
                print("pingRain #", ii)
                newmsgcontent = await ctx.fetch_message(msgid)
                if checklove in newmsgcontent.content:
                    await hook.send("Please give me some love "+usermention.mention+" :'(")
                    await asyncio.sleep(random.randint(10, 45))
                else:
                    return await hook.send("Thanks for having fun with us "+usermention.mention+" :')")
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

