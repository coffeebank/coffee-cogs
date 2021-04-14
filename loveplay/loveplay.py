from redbot.core import Config, commands, checks
from urllib.request import urlopen
import discord
import asyncio
import random
import requests
import json

class Loveplay(commands.Cog):
    """Send love to other members of the server with hugs, kisses, etc."""

    def __init__(self):
        self.config = Config.get_conf(self, identifier=806715409318936616)

    async def red_get_data_for_user(self, *, user_id: int):
        # this cog does not story any data
        return {}

    async def red_delete_data_for_user(self, *, requester, user_id: int) -> None:
        # this cog does not story any data
        pass


    # Utility Commands

    def purrbotApi(self, topic, mincount:int, maxcount:int, gifImg, filetype):
        # Check for file integrity locally
        url = "https://purrbot.site/img/sfw/{2}/{0}/{2}_0{1}.{3}".format(gifImg, random.randint(mincount, maxcount), topic, filetype)
        status_code = self.checkAlive(url)

        if status_code == False:
            reqdata = requests.get("https://purrbot.site/api/img/sfw/{0}/{1}".format(topic,gifImg)).json()
            return reqdata["link"]
        else:
            return status_code

    def checkAlive(self, url):
        if urlopen(url).getcode() == 200:
            return url
        else:
            return False

    async def buildEmbed(self, ctx, descriptor, imgUrl, text=None):
        if text == None:
            desc = ""
        else:
            desc = "**{0}**\u2002gives **{1}** a {2}".format(ctx.author.display_name, text, descriptor)
        botcolor = await ctx.embed_colour()
        e = discord.Embed(color=botcolor, description=desc)
        e.set_image(url=imgUrl)
        e.set_footer(text="Made with Purrbot API\u2002💌")
        return e


    # Bot Commands
 
    @commands.command(name="blush")
    async def lpblush(self, ctx, user):
        """Send a blush"""
        desc = "blush"
        src = self.purrbotApi(desc, 10, 60, "gif", "gif")
        e = await self.buildEmbed(ctx, desc, src, user)
        await ctx.send(embed=e)

    @commands.command(name="dance")
    async def lpdance(self, ctx, user):
        """Send a dance"""
        desc = "dance"
        src = self.purrbotApi(desc, 10, 60, "gif", "gif")
        e = await self.buildEmbed(ctx, desc, src, user)
        await ctx.send(embed=e)
        
    @commands.command(name="hug")
    async def lphug(self, ctx, user):
        """Send a hug"""
        desc = "hug"
        src = self.purrbotApi(desc, 10, 60, "gif", "gif")
        e = await self.buildEmbed(ctx, desc, src, user)
        await ctx.send(embed=e)
        
    @commands.command(name="kiss")
    async def lpkiss(self, ctx, user):
        """Send a kiss"""
        desc = "kiss"
        src = self.purrbotApi(desc, 10, 60, "gif", "gif")
        e = await self.buildEmbed(ctx, desc, src, user)
        await ctx.send(embed=e)
        
    @commands.command(name="lick")
    async def lplick(self, ctx, user):
        """Send a lick"""
        desc = "lick"
        src = self.purrbotApi(desc, 10, 60, "gif", "gif")
        e = await self.buildEmbed(ctx, desc, src, user)
        await ctx.send(embed=e)
        
    @commands.command(name="neko")
    async def lpneko(self, ctx, user):
        """Send a neko"""
        desc = "neko"
        src = self.purrbotApi(desc, 10, 60, "gif", "gif")
        e = await self.buildEmbed(ctx, desc, src, user)
        await ctx.send(embed=e)
        
    @commands.command(name="pat")
    async def lppat(self, ctx, user):
        """Send a pat"""
        desc = "pat"
        src = self.purrbotApi(desc, 10, 60, "gif", "gif")
        e = await self.buildEmbed(ctx, desc, src, user)
        await ctx.send(embed=e)
        
    @commands.command(name="poke")
    async def lppoke(self, ctx, user):
        """Send a poke"""
        desc = "poke"
        src = self.purrbotApi(desc, 10, 60, "gif", "gif")
        e = await self.buildEmbed(ctx, desc, src, user)
        await ctx.send(embed=e)
        
    @commands.command(name="slap")
    async def lpslap(self, ctx, user):
        """Send a slap"""
        desc = "slap"
        src = self.purrbotApi(desc, 10, 60, "gif", "gif")
        e = await self.buildEmbed(ctx, desc, src, user)
        await ctx.send(embed=e)
        
    @commands.command(name="yuri")
    @commands.is_nsfw()
    async def lpyuri(self, ctx, user):
        """Send a yuri"""
        desc = "yuri"
        req = requests.get("https://purrbot.site/api/img/nsfw/yuri/gif").json()
        src = req["link"]
        e = await self.buildEmbed(ctx, desc, src, user)
        await ctx.send(embed=e)
        