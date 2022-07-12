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
            "leaveEnabled": False,
            "leaveWebhook": "",
            "leaveMessage": {},
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

    async def hellohookSender(self, webhook, userObj: discord.Member, greetMessage):
        # Isolate greetMessage from hellohookSender, and have it be passed in as argument
        # greetMessage = await self.config.guild(userObj.guild).greetMessage()

        # Replace with content
        greetMessageStr = str(json.dumps(greetMessage))
        if "https://&&USERAVATAR&&" in greetMessageStr:
            greetMessageStr = greetMessageStr.replace("https://&&USERAVATAR&&", str(userObj.avatar_url))
        if "https://&&USERMENTION&&" in greetMessageStr:
            greetMessageStr = greetMessageStr.replace("https://&&USERMENTION&&", str(userObj.mention))
        if "https://&&USERNAME&&" in greetMessageStr:
            greetMessageStr = greetMessageStr.replace("https://&&USERNAME&&", str(userObj.name))
        if "https://&&USERNAME1234&&" in greetMessageStr:
            greetMessageStr = greetMessageStr.replace("https://&&USERNAME1234&&", str(userObj.name)+"#"+str(userObj.discriminator))
        if "https://&&SERVERCOUNT&&" in greetMessageStr:
            greetMessageStr = greetMessageStr.replace("https://&&SERVERCOUNT&&", str(userObj.guild.member_count))
        if "https://&&SERVERCOUNTORD&&" in greetMessageStr:
            greetMessageStr = greetMessageStr.replace("https://&&SERVERCOUNTORD&&", str(self.ordinalize_num(userObj.guild.member_count)))
        greetMessageJson = json.loads(str(greetMessageStr))
        # Patch fix: send() got an unexpected keyword argument 'attachments'
        if "attachments" in greetMessageJson:
            greetMessageJson.pop("attachments")
        # Create embed
        if greetMessageJson["embeds"]:
            e = discord.Embed.from_dict(greetMessageJson["embeds"][0])
            greetMessageJson["embeds"] = [e]
        # Send webhook
        try:
            return await webhook.send(**greetMessageJson)
        except Exception as e:
            return print(e)

    def ordinalize_num(self, n):
        # https://stackoverflow.com/a/50992575/15923512 CC BY-SA 4.0
        n = int(n)
        if 11 <= (n % 100) <= 13:
            suffix = 'th'
        else:
            suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
        return str(n) + suffix

    def validChecker(self, item):
        if item:
            return item
        else:
            return None


    # Bot Commands

    @commands.guild_only()
    @commands.group()
    @checks.admin_or_permissions(manage_guild=True)
    async def hellohook(self, ctx: commands.Context):
        """Hellohook settings

        **`[p]hellohook settings`**\u2002View current settings
        
        **`[p]hellohook setgreet`**\u2002Set a Greet/welcome message
        **`[p]hellohook setgreethook`**\u2002 Set #channel for Greet message

        **`[p]hellohook setleave`**\u2002Set a Leave message
        **`[p]hellohook setleavehook`**\u2002 Set #channel for Leave message
        
        Due to Discord limitations, you will have to create a webhook yourself in the channel you want the welcome message in. See **`[p]hellohook setgreethook`** for more details.
        
        [See Documentation >](https://github.com/coffeebank/coffee-cogs/wiki/Hellohook)
        """
        if not ctx.invoked_subcommand:
            pass

    @hellohook.command(name="settings")
    async def hellohooksettings(self, ctx):
        """See current Hellohook settings"""
        guildData = await self.config.guild(ctx.guild).all()

        # Greet info
        e = discord.Embed(color=(await ctx.embed_colour()), title="Hellohook Greet Settings")
        e.add_field(name="Greet Enabled", value=guildData.get("hellohookEnabled", None), inline=False)
        e.add_field(name="Greet Webhook", value=self.validChecker(guildData.get("greetWebhook", None)), inline=False)
        e.add_field(name="Greet Message", value='```json\n'+str(json.dumps(guildData.get("greetMessage", {})))+'```', inline=False)
        await ctx.send(embed=e)

        # Leave info
        e2 = discord.Embed(color=(await ctx.embed_colour()), title="Hellohook Leave Settings")
        e2.add_field(name="Leave Enabled", value=guildData.get("leaveEnabled", None), inline=False)
        e2.add_field(name="Leave Webhook", value=self.validChecker(guildData.get("leaveWebhook", None)), inline=False)
        e2.add_field(name="Leave Message", value='```json\n'+str(json.dumps(guildData.get("leaveMessage", {})))+'```', inline=False)
        await ctx.send(embed=e2)
    
    @hellohook.command(name="setgreethook", aliases=["set", "setchannel", "setwebhook"])
    async def hellohooksetgreethook(self, ctx, webhookUrl):
        """Set the webhook URL/channel for Greet messages
        
        Must be webhook URL. Due to Discord limitations, you will have to make the webhook yourself. You can create a webhook in your desired channel by:
        
        #channel ⚙ settings > Integrations > Webhooks > New Webhook

        [How to create a webhook (image) >](https://support.discord.com/hc/article_attachments/1500000463501/Screen_Shot_2020-12-15_at_4.41.53_PM.png)

        After you create the webhook, you can customize the profile picture and name of the "bot", which will be used when Hellohook sends a message.
        """
        if "https://" in webhookUrl:
          await self.config.guild(ctx.guild).greetWebhook.set(webhookUrl)
          await ctx.message.add_reaction("✅")
        else:
          await ctx.send("Error: Please enter a webhook URL!")
    
    @hellohook.command(name="setleavehook")
    async def hellohooksetleavehook(self, ctx, webhookUrl):
        """Set the webhook URL/channel for Leave messages
        
        Must be webhook URL. Due to Discord limitations, you will have to make the webhook yourself. You can create a webhook in your desired channel by:
        
        #channel ⚙ settings > Integrations > Webhooks > New Webhook

        [How to create a webhook (image) >](https://support.discord.com/hc/article_attachments/1500000463501/Screen_Shot_2020-12-15_at_4.41.53_PM.png)

        After you create the webhook, you can customize the profile picture and name of the "bot", which will be used when Hellohook sends a message.
        """
        if "https://" in webhookUrl:
          await self.config.guild(ctx.guild).leaveWebhook.set(webhookUrl)
          await ctx.message.add_reaction("✅")
        else:
          await ctx.send("Error: Please enter a webhook URL!")

    @hellohook.command(name="setgreet", aliases=["setwelcome"])
    async def hellohooksetgreet(self, ctx, *, DiscohookJSON: str):
        """Set the Greet message

        The message must be a `{ "content": …, "embeds": [{}] }` object.
        
        You can use variables to put the info of new users into the welcome message automatically.
        
        [Create a webhook message here >\nSee Hellohook help documentation >](https://github.com/coffeebank/coffee-cogs/wiki/Hellohook)

        When you are done on Discohook:
        - Scroll to the bottom
        - Click "JSON Data Editor"
        - Click "Copy to Clipboard"
        - Paste it into this bot command
        """
        welcomeMsg = json.loads(DiscohookJSON)
        await self.config.guild(ctx.guild).greetMessage.set(welcomeMsg)
        await ctx.message.add_reaction("✅")

    @hellohook.command(name="setleave")
    async def hellohooksetleave(self, ctx, *, DiscohookJSON: str):
        """Set the Leave message

        The message must be a `{ "content": …, "embeds": [{}] }` object.
        
        You can use variables to put the info of users into the message automatically.
        
        [Create a webhook message here >\nSee Hellohook help documentation >](https://github.com/coffeebank/coffee-cogs/wiki/Hellohook)

        When you are done on Discohook:
        - Scroll to the bottom
        - Click "JSON Data Editor"
        - Click "Copy to Clipboard"
        - Paste it into this bot command
        """
        welcomeMsg = json.loads(DiscohookJSON)
        await self.config.guild(ctx.guild).leaveMessage.set(welcomeMsg)
        await ctx.message.add_reaction("✅")
    
    @hellohook.command(name="test")
    async def hellohooktest(self, ctx):
        """Send a test welcome message to the hellohook"""
        try:
            # Greet Messages
            hellohookEnabled = await self.config.guild(ctx.guild).hellohookEnabled()
            greetWebhook = await self.config.guild(ctx.guild).greetWebhook()
            greetMessage = await self.config.guild(ctx.message.guild).greetMessage()

            # Leave Messages
            leaveEnabled = await self.config.guild(ctx.guild).leaveEnabled()
            leaveWebhook = await self.config.guild(ctx.guild).leaveWebhook()
            leaveMessage = await self.config.guild(ctx.message.guild).leaveMessage()

            # Confirm
            await ctx.send("Hellohook Greet Enabled: "+str(hellohookEnabled))
            await ctx.send("Hellohook Leave Enabled: "+str(leaveEnabled))

            # Send Webhooks
            async with aiohttp.ClientSession() as session:
                try:
                  greetWebhook = Webhook.from_url(greetWebhook, adapter=AsyncWebhookAdapter(session))
                  await self.hellohookSender(greetWebhook, ctx.message.author, greetMessage)
                except:
                  await ctx.send("Error: Hellohook Greet message failed. Is your webhook deleted, or your message empty?")

                try:
                  leaveWebhook = Webhook.from_url(leaveWebhook, adapter=AsyncWebhookAdapter(session))
                  await self.hellohookSender(leaveWebhook, ctx.message.author, leaveMessage)
                except:
                  await ctx.send("Error: Hellohook Leave message failed. Is your webhook deleted, or your message empty?")

        except Exception as e:
            await ctx.send("Error: "+str(e))
        
    @hellohook.command(name="toggle")
    async def hellohooktoggle(self, ctx, GreetOrLeave: str, TrueOrFalse: bool):
        """Enable/Disable Hellohook Greet/Leave messages
        
        [p]hellohook toggle greet true -> enable Greet messages
        [p]hellohook toggle greet false -> disable Greet messages

        [p]hellohook toggle leave true -> enable Leave messages
        [p]hellohook toggle leave false -> disable Leave messages
        """
        if GreetOrLeave == "greet":
          await self.config.guild(ctx.guild).hellohookEnabled.set(TrueOrFalse)
          return await ctx.send("Hellohook Greet Messages is now set to "+str(TrueOrFalse))
        elif GreetOrLeave == "leave":
          await self.config.guild(ctx.guild).leaveEnabled.set(TrueOrFalse)
          return await ctx.send("Hellohook Leave Messages is now set to "+str(TrueOrFalse))
        else:
          return await ctx.send("Error: Please specify whether you want to toggle Greet or Leave messages.")
    
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
            await self.hellohookSender(webhook, userObj, greetMessage)
        return

    @commands.Cog.listener()
    async def on_member_remove(self, userObj: discord.Member) -> None:
        # Ignore if it's a bot
        if userObj.bot:
            return

        # Ignore if hellohook is disabled in the user's guild
        userGuild = userObj.guild
        leaveEnabled = await self.config.guild(userGuild).leaveEnabled()
        if leaveEnabled == False:
            return

        leaveMessage = await self.config.guild(userGuild).leaveMessage()
        if not leaveMessage:
            return
        leaveWebhook = await self.config.guild(userGuild).leaveWebhook()
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(leaveWebhook, adapter=AsyncWebhookAdapter(session))
            await self.hellohookSender(webhook, userObj, leaveMessage)
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
