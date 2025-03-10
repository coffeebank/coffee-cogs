from redbot.core import commands
import aiohttp
import asyncio
import discord
import random
import json

import logging
logger = logging.getLogger(__name__)

class Loveplay(commands.Cog):
    """Send love to other members of the server with hugs, kisses, etc."""

    def __init__(self):
        self.config = None

    # This cog does not store any End User Data
    async def red_get_data_for_user(self, *, user_id: int):
        return {}
    async def red_delete_data_for_user(self, *, requester, user_id: int) -> None:
        pass


    # Utility Commands

    def purrbotApi(self, topic, mincount:int, maxcount:int, gifImg, filetype):
        url = "https://purrbot.site/img/sfw/{2}/{0}/{2}_{1}.{3}".format(gifImg, format(random.randint(mincount, maxcount), '03'), topic, filetype)

        # Immediately return generated url whether the link is a real image or not
        return url

        # Check for file integrity, fallback to online API
        # 2021-04-14 - Removing bc load times take too long
        # 2025-03-09 - TODO Migrate to async before restoring (removed requests, urllib.request.urlopen)

        # status_code = self.checkAlive(url)

        # if status_code == False:
        #     reqdata = requests.get("https://purrbot.site/api/img/sfw/{0}/{1}".format(topic,gifImg)).json()
        #     return reqdata["link"]
        # else:
        #     return status_code

        # def checkAlive(self, url):
        #     meta = urlopen(url).info()
        #     if "image" in meta["content-type"]:
        #         return url
        #     else:
        #         return url

    async def fetch_url(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    logger.error(f"Failed to fetch {url}. Status code: {resp.status}")
                    return None
                try:
                    reqdata = await resp.json()
                    return reqdata
                except aiohttp.ClientError as e:
                    logger.error(f"An error occurred while parsing JSON: {e}")
                    return None

    async def buildEmbed(self, ctx, descriptor, imgUrl, text=None):
        if text == None:
            desc = ""
        else:
            desc = "**{0}** gives **{1}** a {2}".format(ctx.author.mention, text, descriptor)
        
        # Add support without embed_links
        if ctx.channel.permissions_for(ctx.guild.me).embed_links:
            botcolor = await ctx.embed_colour()
            e = discord.Embed(color=botcolor, description=desc)
            e.set_image(url=imgUrl)
            e.set_footer(text="Made with Purrbot API\u2002💌")
            return await ctx.send(embed=e)
        else:
            return await ctx.send(desc+"\n"+imgUrl+" - "+"_Made with Purrbot API\u2002💌_")


    # Bot Commands
 
    @commands.hybrid_command(name="loveplay", aliases=["lp"])
    async def lpmain(self, ctx, action, description, *, user):
        """Send a custom lovely reaction to someone!

        Type  **`[p]help Loveplay`**  to see built-in reactions.

        **`action`**  :  A sfw gif action from [Purrbot Image API](https://docs.purrbot.site/api/)
        **`description`**  :  @you gives @user a *"description"* (quotes if multi-word)

        [Loveplay Documentation >](https://coffeebank.github.io/coffee-cogs/loveplay)"""
        src = self.purrbotApi(action, 1, 20, "gif", "gif")
        e = await self.buildEmbed(ctx, description, src, user)
        return # Sent in buildEmbed
 
    @commands.hybrid_command(name="blush")
    async def lpblush(self, ctx, *, user):
        """Send a blush"""
        desc = "blush"
        src = self.purrbotApi(desc, 1, 20, "gif", "gif")
        e = await self.buildEmbed(ctx, desc, src, user)
        return # Sent in buildEmbed

    @commands.hybrid_command(name="cuddle")
    async def lpcuddle(self, ctx, *, user):
        """Send a cuddle"""
        desc = "cuddle"
        src = self.purrbotApi(desc, 1, 20, "gif", "gif")
        e = await self.buildEmbed(ctx, desc, src, user)
        return # Sent in buildEmbed

    @commands.hybrid_command(name="dance")
    async def lpdance(self, ctx, *, user):
        """Send a dance"""
        desc = "dance"
        src = self.purrbotApi(desc, 1, 20, "gif", "gif")
        e = await self.buildEmbed(ctx, desc, src, user)
        return # Sent in buildEmbed
        
    @commands.hybrid_command(name="feed", aliases=["cookie"])
    async def lpfeed(self, ctx, *, user):
        """Send some food/cookie
        
        Formerly the `[p]nom` command"""
        desc = "feed"
        src = self.purrbotApi(desc, 1, 18, "gif", "gif")
        e = await self.buildEmbed(ctx, "yummy cookie", src, user)
        return # Sent in buildEmbed
        
    @commands.hybrid_command(name="hugs", aliases=["hug"])
    async def lphug(self, ctx, *, user):
        """Send a hug"""
        desc = "hug"
        src = self.purrbotApi(desc, 1, 60, "gif", "gif")
        e = await self.buildEmbed(ctx, desc, src, user)
        return # Sent in buildEmbed
        
    @commands.hybrid_command(name="kiss")
    async def lpkiss(self, ctx, *, user):
        """Send a kiss"""
        desc = "kiss"
        src = self.purrbotApi(desc, 1, 60, "gif", "gif")
        e = await self.buildEmbed(ctx, desc, src, user)
        return # Sent in buildEmbed
        
    @commands.hybrid_command(name="lick")
    async def lplick(self, ctx, *, user):
        """Send a lick"""
        desc = "lick"
        src = self.purrbotApi(desc, 1, 16, "gif", "gif")
        e = await self.buildEmbed(ctx, desc, src, user)
        return # Sent in buildEmbed
        
    @commands.hybrid_command(name="neko")
    async def lpneko(self, ctx, *, user):
        """Send a neko"""
        desc = "neko"
        src = self.purrbotApi(desc, 1, 20, "gif", "gif")
        e = await self.buildEmbed(ctx, desc, src, user)
        return # Sent in buildEmbed
        
    @commands.hybrid_command(name="nom")
    async def lpnom(self, ctx, *, user):
        """Send a nom
        
        The old command for feeding a user has moved to `[p]feed`"""
        desc = "bite"
        src = self.purrbotApi(desc, 1, 24, "gif", "gif")
        e = await self.buildEmbed(ctx, "yummy nom <a:vampynom:815998604945653771>", src, user)
        return # Sent in buildEmbed
        
    @commands.hybrid_command(name="pat")
    async def lppat(self, ctx, *, user):
        """Send a pat"""
        desc = "pat"
        src = self.purrbotApi(desc, 1, 20, "gif", "gif")
        e = await self.buildEmbed(ctx, desc, src, user)
        return # Sent in buildEmbed
        
    @commands.hybrid_command(name="poke")
    async def lppoke(self, ctx, *, user):
        """Send a poke"""
        desc = "poke"
        src = self.purrbotApi(desc, 1, 20, "gif", "gif")
        e = await self.buildEmbed(ctx, desc, src, user)
        return # Sent in buildEmbed
        
    @commands.hybrid_command(name="slap")
    async def lpslap(self, ctx, *, user):
        """Send a slap"""
        desc = "slap"
        src = self.purrbotApi(desc, 1, 20, "gif", "gif")
        e = await self.buildEmbed(ctx, desc, src, user)
        return # Sent in buildEmbed
        
    @commands.hybrid_command(name="yuri")
    @commands.is_nsfw()
    async def lpyuri(self, ctx, *, user):
        """Send a yuri"""
        desc = "yuri"
        req = await self.fetch_url("https://purrbot.site/api/img/nsfw/yuri/gif")
        src = req.get("link", "") # Silently fail if no image returned
        e = await self.buildEmbed(ctx, desc, src, user)
        return # Sent in buildEmbed
        
