from redbot.core import Config, commands, checks
from redbot.cogs.admin import admin
import asyncio
import aiohttp
import discord
from discord import Webhook, AsyncWebhookAdapter
from urllib.parse import quote
import json

class Hellohook(commands.Cog):
    """Gives you links to common search engines based on a search query."""

    def __init__(self, bot):
        self.config = Config.get_conf(self, identifier=806715409318936616)
        self.bot = bot
        default_guild = {
            "hellohookEnabled": False,
            "greetWebhook": "",
            "greetUserMention": False,
            "embedColor": None,
            "embedAuthor": {
                "authorField": None,
                "authorIconUrl": None,
                "authorLink": ""
            },
            "embedDescription": None,
        }
        self.config.register_guild(**default_guild)


    async def red_get_data_for_user(self, *, user_id: int):
        # this cog does not story any data
        return {}

    async def red_delete_data_for_user(self, *, requester, user_id: int) -> None:
        # this cog does not story any data
        pass


    # Utility Commands

    async def hellohookSender(self, webhook, userObj: discord.Member):
        greetUserMention = await self.config.guild(userObj.guild).greetUserMention()
        embedAuthor = await self.config.guild(userObj.guild).embedAuthor()
        embedDescription = await self.config.guild(userObj.guild).embedDescription()

        if greetUserMention == True:
            msgContent = userObj.mention
        else:
            msgContent = ""

        e = discord.Embed(color=discord.Color(value=0x25c059), description=embedDescription)
        e.set_author(name=embedAuthor["authorField"], icon_url=embedAuthor["authorIconUrl"], url=embedAuthor["authorLink"])

        await webhook.send(
            msgContent, 
            embed=e
        )


    # Bot Commands

    @commands.guild_only()
    @commands.group()
    @checks.admin_or_permissions(manage_guild=True)
    async def hellohook(self, ctx: commands.Context):
        """Hellohook settings
        
        For help popups in each command, type `[p]help hellohook commandhere`"""
        if not ctx.invoked_subcommand:
            pass
    
    @hellohook.command(name="toggle")
    async def hellohooktoggle(self, ctx, TrueOrFalse: bool):
        """Enable/Disable Hellohook welcomes"""
        await self.config.guild(ctx.guild).hellohookEnabled.set(TrueOrFalse)
        await ctx.send("Hellohook is now set to "+str(TrueOrFalse))
    
    @hellohook.command(name="test")
    async def hellohooktest(self, ctx):
        """Send a test welcome message to the hellohook"""
        hellohookEnabled = await self.config.guild(ctx.guild).hellohookEnabled()
        greetUserMention = await self.config.guild(ctx.guild).greetUserMention()
        greetWebhook = await self.config.guild(ctx.guild).greetWebhook()
        # Send Webhook
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(greetWebhook, adapter=AsyncWebhookAdapter(session))
            await self.hellohookSender(webhook, ctx.message.author)
        # Confirm
        await ctx.message.add_reaction("✅")
        await ctx.send("hellohookEnabled: "+str(hellohookEnabled)+"\n"+"greetUserMention: "+str(greetUserMention))
    
    @hellohook.command(name="setclear")
    async def hellohooksetclear(self, ctx, TypeTrueToConfirm: bool):
        """⚠️ Reset all settings"""
        await self.config.guild(ctx.guild).hellohookEnabled.set(False)
        await self.config.guild(ctx.guild).greetWebhook.set("")
        await self.config.guild(ctx.guild).greetUserMention.set(False)
        await self.config.guild(ctx.guild).embedColor.set(None)
        await self.config.guild(ctx.guild).embedAuthor.set({
            "authorField": None,
            "authorIconUrl": None,
            "authorLink": None
        })
        await self.config.guild(ctx.guild).embedDescription.set(None)
        await ctx.message.add_reaction("✅")
    
    @hellohook.command(name="setchannel")
    async def hellohooksetchannel(self, ctx, webhookUrl):
        """Set the webhook url to send the welcome message to"""
        await self.config.guild(ctx.guild).greetWebhook.set(webhookUrl)
        await ctx.message.add_reaction("✅")
    
    @hellohook.command(name="setmention")
    async def hellohooksetmention(self, ctx, TrueOrFalse: bool):
        """Set whether to @ping the user in the message"""
        await self.config.guild(ctx.guild).greetUserMention.set(TrueOrFalse)
        await ctx.message.add_reaction("✅")
    
    # @hellohook.command(name="embedcolor", aliases=["embedcolour"])
    # async def hellohookembedcolor(self, ctx):
    #     """Set embed color"""
    #     await self.config.guild(ctx.guild).embedColor.set()
    #     await ctx.message.add_reaction("✅")
    
    @hellohook.command(name="embedauthor")
    async def hellohookembedauthor(self, ctx, authorField=None, authorIconUrl=None, authorLink=""):
        """Set embed's author
        
        Draft your embed code on https://discohook.org"""
        embedAuthor = await self.config.guild(ctx.guild).embedAuthor()
        embedAuthor["authorField"] = authorField
        embedAuthor["authorIconUrl"] = authorIconUrl
        embedAuthor["authorLink"] = authorLink
        await self.config.guild(ctx.guild).embedAuthor.set(embedAuthor)
        await ctx.message.add_reaction("✅")
    
    @hellohook.command(name="embeddescription")
    async def hellohookembeddescription(self, ctx, *, embedDescription):
        """Set embed's description
        
        Draft your embed code on https://discohook.org"""
        await self.config.guild(ctx.guild).embedDescription.set(embedDescription)
        await ctx.message.add_reaction("✅")

    
    # Listeners

    @commands.Cog.listener()
    async def on_member_join(self, userObj: discord.Member) -> None:
        # Ignore if it's a bot
        if userObj.bot:
            return

        # Ignore if hellohook is disabled in the user's guild
        userGuild = userObj.guild
        hellohookEnabled = await self.config.guild(userGuild).hellohookEnabled()
        if hellohookEnabled == False:
            return

        greetWebhook = await self.config.guild(userGuild).greetWebhook()
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(greetWebhook, adapter=AsyncWebhookAdapter(session))
            await self.hellohookSender(webhook, userObj)
        return
        

