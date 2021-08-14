from redbot.core import Config, commands, checks
from redbot.cogs.admin import admin
import asyncio
import aiohttp
import discord
from discord import Webhook, AsyncWebhookAdapter
from urllib.parse import quote
import json
import typing

class Hellohook(commands.Cog):
    """Custom welcome message bots"""

    def __init__(self, bot):
        self.config = Config.get_conf(self, identifier=806715409318936616)
        self.bot = bot
        default_guild = {
            "hellohookEnabled": False,
            "greetWebhook": "",
            "greetMessage": {},
            # "greetUserMention": False,
            # "embedAuthor": {
            #     "authorField": None,
            #     "authorIconUrl": None,
            #     "authorLink": None
            # },
            # "embedDescription": None,
        }
        self.config.register_guild(**default_guild)

    # This cog does not store any End User Data
    async def red_get_data_for_user(self, *, user_id: int):
        return {}
    async def red_delete_data_for_user(self, *, requester, user_id: int) -> None:
        pass


    # Utility Commands

    async def hellohookSender(self, webhook, userObj: discord.Member):
        greetMessage = await self.config.guild(userObj.guild).greetMessage()
        # Replace with content
        greetMessageStr = str(json.dumps(greetMessage))
        if "https://&&USERAVATAR&&" in greetMessageStr:
            greetMessageStr = greetMessageStr.replace("https://&&USERAVATAR&&", userObj.avatar_url)
        if "https://&&USERMENTION&&" in greetMessageStr:
            greetMessageStr = greetMessageStr.replace("https://&&USERMENTION&&", userObj.mention)
        if "https://&&USERNAME&&" in greetMessageStr:
            greetMessageStr = greetMessageStr.replace("https://&&USERNAME&&", str(userObj.name))
        if "https://&&USERNAME1234&&" in greetMessageStr:
            greetMessageStr = greetMessageStr.replace("https://&&USERNAME1234&&", str(userObj.name)+"#"+str(userObj.discriminator))
        greetMessageJson = json.loads(str(greetMessageStr))
        # Create embed
        if greetMessageJson["embeds"]:
            e = discord.Embed.from_dict(greetMessageJson["embeds"][0])
            greetMessageJson["embeds"] = [e]
        # Send webhook
        try:
            return await webhook.send(**greetMessageJson)
        except Exception as e:
            return print(e)

    def validChecker(self, item):
        if item:
            return item
        else:
            return None

    async def webhookCheckInput(self, ctx, toChannel):
        # Find/create webhook at destination if input is a channel
        if isinstance(toChannel, discord.TextChannel):
            toWebhook = await self.webhookFinder(toChannel)
            if toWebhook == False:
                await ctx.send("An error occurred: could not create webhook. Am I missing permissions?")
                return False
            return toWebhook
        # Use webhook url as-is if there is https link (doesn't have to be Discord)
        if "https://" in toChannel:
            return str(toChannel)
        # Error likely occurred, return False
        await ctx.send("Error: Channel is not in this server, or webhook URL is invalid.")
        return False

    async def webhookFinder(self, channel):
        # Find a webhook that the bot made
        try:
            whooklist = await channel.webhooks()
        except:
            return False
        # Return if match
        for wh in whooklist:
            if self.bot.user == wh.user:
                return wh.url
        # If the function got here, it means there isn't one that the bot made
        try:
            newHook = await channel.create_webhook(name="Webhook")
            return newHook.url
        # Could not create webhook, return False
        except:
            return False


    # Bot Commands

    @commands.guild_only()
    @commands.group()
    @checks.admin_or_permissions(manage_guild=True)
    async def hellohook(self, ctx: commands.Context):
        """Hellohook settings
        
        Data has been upgraded to V2 system. See **`[p]hellohook set`** for more info."""
        if not ctx.invoked_subcommand:
            guildData = await self.config.guild(ctx.guild).all()
            e = discord.Embed(color=(await ctx.embed_colour()), title="Hellohook Settings")
            e.add_field(name="Greet Enabled", value=guildData.get("hellohookEnabled", None), inline=False)
            e.add_field(name="Greet Webhook", value=self.validChecker(guildData.get("greetWebhook", None)), inline=False)
            e.add_field(name="Greet Message", value='```json\n'+str(json.dumps(guildData.get("greetMessage", {})))+'```', inline=False)
            await ctx.send(embed=e)
            # pass
    
    @hellohook.command(name="setchannel")
    async def hellohooksetchannel(self, ctx, channel: typing.Union[discord.TextChannel, str]):
        """Set the channel to send the welcome message to
        
        #channel or webhook URL accepted."""
        # Error catching
        toWebhook = await self.webhookCheckInput(ctx, channel)
        if toWebhook == False:
            return
        await self.config.guild(ctx.guild).greetWebhook.set(toWebhook)
        if isinstance(channel, discord.TextChannel):
            await ctx.send("Webhook successfully created. Be sure to go into channel settings and edit `Webhook` created by the bot, to add a custom Name and Profile Picture!")
        await ctx.message.add_reaction("✅")
        
    @hellohook.command(name="toggle")
    async def hellohooktoggle(self, ctx, TrueOrFalse: bool):
        """Enable/Disable Hellohook welcomes"""
        await self.config.guild(ctx.guild).hellohookEnabled.set(TrueOrFalse)
        await ctx.send("Hellohook is now set to "+str(TrueOrFalse))
    
    @hellohook.command(name="test")
    async def hellohooktest(self, ctx):
        """Send a test welcome message to the hellohook"""
        try:
            hellohookEnabled = await self.config.guild(ctx.guild).hellohookEnabled()
            greetWebhook = await self.config.guild(ctx.guild).greetWebhook()
            # Send Webhook
            async with aiohttp.ClientSession() as session:
                webhook = Webhook.from_url(greetWebhook, adapter=AsyncWebhookAdapter(session))
                await self.hellohookSender(webhook, ctx.message.author)
            # Confirm
            await ctx.send("hellohookEnabled: "+str(hellohookEnabled))
        except Exception as e:
            await ctx.send("Error: "+str(e))

    @hellohook.command(name="set", aliases=["setwelcome"])
    async def hellohooksetwelcome(self, ctx, *, DiscohookJSON: str):
        """Set the hellohook welcome

        Welcome message must be a `{"embeds":[{}]}` object. Discohook is a website for drafting webhooks, and is not affiliated with this cog.
        
        [Click here to create your webhook message using Discohook >](https://discohook.org/?data=eyJtZXNzYWdlcyI6W3siZGF0YSI6eyJjb250ZW50IjpudWxsLCJlbWJlZHMiOlt7InRpdGxlIjoiVGl0bGUgU2FtcGxlIiwiZGVzY3JpcHRpb24iOiJEZXNjcmlwdGlvbiBTYW1wbGUiLCJjb2xvciI6MTAwNjYzNjMsImF1dGhvciI6eyJuYW1lIjoiQXV0aG9yIFNhbXBsZSJ9LCJmb290ZXIiOnsidGV4dCI6IkZvb3RlciBTYW1wbGUifSwiaW1hZ2UiOnsidXJsIjoiaHR0cHM6Ly9jZG4uZGlzY29yZGFwcC5jb20vYXR0YWNobWVudHMvODc1OTA3MTU3ODUyMjk5Mjc0Lzg3NTkwNzQ3NzIzNTk4MjM1Ni91bnNwbGFzaC5jb20tcGhvdG9zLVg0NUd5SXBqcFpjLmpwZyJ9fV19fV19)
        [Click here to see user variables >](https://github.com/coffeebank/coffee-cogs/wiki/Hellohook)

        When you are done on Discohook:
        - Scroll to the bottom
        - Click "JSON Data Editor"
        - Click "Copy to Clipboard"
        - Paste it into this bot command
        """
        welcomeMsg = json.loads(DiscohookJSON)
        await self.config.guild(ctx.guild).greetMessage.set(welcomeMsg)
        await ctx.message.add_reaction("✅")
    
    @hellohook.command(name="reset")
    async def hellohooksetclear(self, ctx, TypeTrueToConfirm: bool):
        """⚠️ Reset all settings"""
        await self.config.guild(ctx.guild).clear_raw()
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

        greetMessage = await self.config.guild(userGuild).greetMessage()
        if not greetMessage:
            updatev1data = await self.updatev1data(userObj.guild)
            if updatev1data == False:
                return
        greetWebhook = await self.config.guild(userGuild).greetWebhook()
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(greetWebhook, adapter=AsyncWebhookAdapter(session))
            await self.hellohookSender(webhook, userObj)
        return
        

    # Legacy

    async def updatev1data(self, guildObj):
        def toContent(a):
            if a == True:
                return "https://&&USERMENTION&&"
            else:
                return None
        greetMessage = await self.config.guild(guildObj).greetMessage()
        if not greetMessage:
            guildData = await self.config.guild(guildObj).all()
            v1migrate = {
                "content": toContent(guildData.get("greetUserMention", None)),
                "embeds": [{
                    "author": {
                        "name": guildData["embedAuthor"].get("authorField", None),
                        "url": guildData["embedAuthor"].get("authorLink", None),
                        "icon_url": guildData["embedAuthor"].get("authorIconUrl", None)
                    },
                    "color": 2474073,
                    "description": guildData.get("embedDescription", None)
                }]
            }
            await self.config.guild(guildObj).greetMessage.set(v1migrate)
            return v1migrate
        else:
            return False
