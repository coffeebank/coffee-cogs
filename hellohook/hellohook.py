from redbot.core import Config, commands, checks
from redbot.cogs.admin import admin
import asyncio
import discord
from discord import Webhook, SyncWebhook, Embed
from urllib.parse import quote
import json
import typing

import logging
logger = logging.getLogger(__name__)

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
            "inviteList": {},
            # {
            #   "id": {
            #     uses: int,
            #     channel: str, // webhook url
            #     message: {} // discohook json
            #     roles: [role.id] // role invites
            #   }
            # }
            "oldInviteList": {}
        }
        self.config.register_guild(**default_guild)
        bot.loop.create_task(self.inviteSync())

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
            greetMessageStr = greetMessageStr.replace("https://&&USERAVATAR&&", str(userObj.display_avatar.url))
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
        if greetMessageJson.get("attachments", False) is not False:
            greetMessageJson.pop("attachments")
        # Create embed
        if greetMessageJson.get("embeds", None) not in ["null", None, []]:
            # For loops not working for some reason? Force patching to add support for 2 embeds
            e = discord.Embed.from_dict(greetMessageJson["embeds"][0])
            try:
                e2 = discord.Embed.from_dict(greetMessageJson["embeds"][1])
                greetMessageJson["embeds"] = [e, e2]
            except:
                greetMessageJson["embeds"] = [e]
        # Send webhook
        try:
            # (MM101) Add custom parameters here

            # (dpy-v2) Sending keys with value of None doesn't work anymore
            return webhook.send(
                **{k: v for k, v in greetMessageJson.items() if v is not None}
            )
        except Exception as err:
            logger.error("Error:", err)
            logger.debug(webhook, userObj, greetMessage)
            return err

    async def inviteFetch(ctx, guildObj, inviteLink: str):
        newInvites = await guildObj.invites()
        try:
            # Must be a full link
            if "discord" in inviteLink:
                invObj = next((nio for nio in newInvites if nio.url == inviteLink), None)
            # Partial invite code
            else:
                invObj = next((nio for nio in newInvites if nio.id == inviteLink), None)
            return invObj
        except:
            return None

    async def inviteSync(self) -> dict:
        allGuilds = await self.config.all_guilds()
        for guildId in allGuilds:
            guildObj = self.bot.get_guild(guildId)
            if guildObj is None:
                continue
            if len(allGuilds[guildObj.id]["inviteList"]) == 0:
                continue
            # Create new inviteList, which means old invites not found are removed
            inviteList = allGuilds[guildObj.id]["inviteList"]
            newInviteList = {}
            newInvites = await guildObj.invites()
            for ni in newInvites:
                try:
                    if inviteList[str(ni.id)]:
                        newInviteList[str(ni.id)] = {
                            "uses": ni.uses,
                            "channel": inviteList[str(ni.id)]["channel"],
                            "message": inviteList[str(ni.id)]["message"],
                        }
                except:
                    pass
            # Replace previous config, cache old one
            return await self.config.guild(guildObj).oldInviteList.set(inviteList)
            return await self.config.guild(guildObj).inviteList.set(newInviteList)

    async def inviteUpdate(ctx, guildObj, inviteLink: str):
        invObj = self.inviteFetch(guildObj, inviteLink)
        invitesArray = await guildObj.invites()
        try:
            # Must be a full link
            if "discord" in inviteLink:
                invObj = next((nio for nio in newInvites if nio.url == inviteLink), None)
            # Partial invite code
            else:
                invObj = next((nio for nio in newInvites if nio.id == inviteLink), None)
            return invObj
        except:
            return None

    async def inviteUsesSetter(self, guildObj, inviteId, uses: int):
        savedInvites = await self.config.guild(guildObj).inviteList()
        try:
            savedInvites[str(inviteId)]["uses"] = uses
            await self.config.guild(guildObj).inviteList.set(savedInvites)
            return True
        except:
            return None

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

        [See Documentation >](https://coffeebank.github.io/coffee-cogs/hellohook)
        """
        if not ctx.invoked_subcommand:
            pass

    @hellohook.command(name="settings", aliases=["list"])
    async def hellohooksettings(self, ctx):
        """List current Hellohook settings"""
        guildData = await self.config.guild(ctx.guild).all()

        # Greet info
        e = discord.Embed(color=(await ctx.embed_colour()), title="Hellohook Greet Settings")
        e.add_field(name="Greet Enabled", value=guildData.get("hellohookEnabled", None), inline=False)
        e.add_field(name="Greet Webhook", value="||"+str(self.validChecker(guildData.get("greetWebhook", None)))+"||", inline=False)
        e.add_field(name="Greet Message", value='```json\n' + str(json.dumps(guildData.get("greetMessage", {})))[:1011]+'```', inline=False)
        await ctx.send(embed=e)

        # Leave info
        e2 = discord.Embed(color=(await ctx.embed_colour()), title="Hellohook Leave Settings")
        e2.add_field(name="Leave Enabled", value=guildData.get("leaveEnabled", None), inline=False)
        e2.add_field(name="Leave Webhook", value="||"+str(self.validChecker(guildData.get("leaveWebhook", None)))+"||", inline=False)
        e2.add_field(name="Leave Message", value='```json\n' + str(json.dumps(guildData.get("leaveMessage", {})))[:1011]+'```', inline=False)
        await ctx.send(embed=e2)

        # Invites info
        if guildData.get("inviteList", None) is not None:
          e3 = discord.Embed(color=(await ctx.embed_colour()), title="Hellohook Invite Settings", description="Invite settings found, use `[p]hellohook invite settings` to show.")
          await ctx.send(embed=e3)

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

        [Create a webhook message here >\nSee Hellohook help documentation >](https://coffeebank.github.io/coffee-cogs/hellohook)

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

        [Create a webhook message here >\nSee Hellohook help documentation >](https://coffeebank.github.io/coffee-cogs/hellohook)

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
            try:
                greetWebhook = SyncWebhook.from_url(greetWebhook)
                await self.hellohookSender(greetWebhook, ctx.message.author, greetMessage)
            except Exception as err:
                logger.error("Error:", err)
                logger.debug(greetWebhook, ctx.message.author, greetMessage)
                await ctx.send("Error: Hellohook Greet message failed. Is your webhook deleted, or your message empty?")
            try:
                leaveWebhook = SyncWebhook.from_url(leaveWebhook)
                await self.hellohookSender(leaveWebhook, ctx.message.author, leaveMessage)
            except Exception as err:
                logger.error("Error:", err)
                logger.debug(leaveWebhook, ctx.message.author, greetMessage)
                await ctx.send("Error: Hellohook Leave message failed. Is your webhook deleted, or your message empty?")
        except Exception as err:
            logger.error("Error:", err)
            logger.debug(
                "hellohookEnabled:", hellohookEnabled,
                "greetWebhook:", greetWebhook,
                "greetMessage:", greetMessage,
                "leaveEnabled:", leaveEnabled,
                "leaveWebhook:", leaveWebhook,
                "leaveMessage:", leaveMessage
            )
            await ctx.send("Error: "+str(err))

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

    @hellohook.group(name="invite", aliases=["inv", "invites"])
    @checks.admin_or_permissions(manage_guild=True)
    async def hhinv(self, ctx: commands.Context):
        """Send custom Hellohook welcomes based on invite URLs (beta)

        -
        ⚠️ **Warning: This feature is still in testing.
        Data loss is possible. Use at your own risk.
        [See Documentation >](https://coffeebank.github.io/coffee-cogs/hellohook)**
        """
        if not ctx.invoked_subcommand:
            pass

    @hhinv.command(name="add")
    async def hhinvadd(self, ctx):
        "Add a custom invite-based welcome"
        inviteList = await self.config.guild(ctx.guild).inviteList()

        # Choose an invite
        invLink = await ctx.send("Please enter only the ##### part of your <https://discord.gg/#####> invite link you want to attach a custom welcome message to:")
        invLinkPred = await ctx.bot.wait_for("message")
        invObj = await self.inviteFetch(ctx.guild, invLinkPred.clean_content)
        if invObj == None:
            return await ctx.send("Error: Couldn't find invite.... is it valid? Setup exited.")

        # Set invite webhook
        invHook = await ctx.send("Please enter the webhook link you'd like to send the custom welcome message to:")
        invHookPred = await ctx.bot.wait_for("message")
        if "https://" not in invHookPred.clean_content:
            return await ctx.send("Error: Invalid link.... setup exited.")

        # Set message
        invMsg = await ctx.send("Please enter the Discohook JSON you'd like to use as your custom welcome message:")
        invMsgPred = await ctx.bot.wait_for("message")
        try:
            invMsgJson = json.loads(invMsgPred.clean_content)
        except Exception as err:
            logger.debug("Error in invite setup invMsg:", err)
            return await ctx.send("Error: Invalid JSON.... setup exited.")

        # Set message
        invRoles = await ctx.send("Please ping any roles you'd like this invite to also add. Type 'none' to skip.")
        invRolesPred = await ctx.bot.wait_for("message")
        invRolesList = [ir.id for ir in invRolesPred.role_mentions]

        try:
            inviteList[str(invObj.id)] = {
                "uses": invObj.uses,
                "channel": invHookPred.clean_content,
                "message": invMsgJson,
                "roles": invRolesList
            }
        except Exception as err:
            logger.debug("Error in invite setup invRoles:", err)
            return await ctx.send("Error: Variables failed.... setup exited.\n"+str(invObj))

        # Return changes
        await self.config.guild(ctx.guild).inviteList.set(inviteList)
        await ctx.send("Done ✅")
        return

    @hhinv.command(name="edit")
    async def hhinvedit(self, ctx, inviteLink: str, field: str, *, updatedContentHere: str):
        """Edit a custom invite-based welcome

        Please input only the ##### part of your <https://discord.gg/#####> invite.
        
        Fields:
          channel - for webhook URL
          message - for Discohook JSON
        """
        inviteList = await self.config.guild(ctx.guild).inviteList()
        try:
            if field == "message":
                updatedContentHere = json.loads(updatedContentHere)
            inviteList[inviteLink][field] = updatedContentHere
            await self.config.guild(ctx.guild).inviteList.set(inviteList)
            return await ctx.message.add_reaction("✅")
        except Exception as err:
            logger.error("Error:", err)
            await ctx.send("Error: Could not update. Did you type it in the format:\nINVITELINKCODE   FIELD   NEW_CONTENT_HERE")

    @hhinv.command(name="remove")
    async def hhinvremove(self, ctx, inviteLink: str):
        """Remove a custom invite-based welcome

        Please input only the ##### part of your <https://discord.gg/#####> invite."""
        inviteList = await self.config.guild(ctx.guild).inviteList()
        invObj = await self.inviteFetch(ctx.guild, inviteLink)
        if invObj is None:
            return await ctx.send("Error: Could not find invite. Is it already deleted? Run `[p]hellohook invite sync` to clean all deleted invites from Hellohook.")
        newInviteList = inviteList.pop(str(invObj.id), None)
        await self.config.guild(ctx.guild).inviteList.set(newInviteList)
        return await ctx.message.add_reaction("✅")

    @hhinv.command(name="sync")
    async def hhinvsync(self, ctx):
        """Re-sync the invite tracker if bot's been offline

        If the bot has gone offline before, run this command to ensure the bot is tracking the right invites.

        Will also remove all server invites that have expired or disappeared."""
        inviteList = await self.config.guild(ctx.guild).inviteList()
        newInviteList = {}
        newInvites = await ctx.guild.invites()
        for ni in newInvites:
            try:
                if inviteList[str(ni.id)]:
                    newInviteList[str(ni.id)] = {
                        "uses": ni.uses,
                        "channel": inviteList[str(ni.id)]["channel"],
                        "message": inviteList[str(ni.id)]["message"],
                        "roles": inviteList[str(ni.id)].get("roles", None),
                    }
            except Exception as err:
                logger.error("Error:", err)
                pass
        # Replace previous config, cache old one
        await self.config.guild(ctx.guild).oldInviteList.set(inviteList)
        await self.config.guild(ctx.guild).inviteList.set(newInviteList)
        return await ctx.message.add_reaction("✅")

    @hhinv.command(name="settings", aliases=["list"])
    async def hhinvsettings(self, ctx):
        "List all invite-based welcomes"
        inviteList = await self.config.guild(ctx.guild).inviteList()
        for io, iv in inviteList.items():
          try:
            e = discord.Embed(color=(await ctx.embed_colour()), title=io)
            e.add_field(name="Uses", value=inviteList[io]["uses"], inline=False)
            e.add_field(name="Webhook", value="||"+str(self.validChecker(inviteList[io]["channel"]))+"||", inline=False)
            e.add_field(name="Greet Message", value='```json\n' + str(json.dumps(inviteList[io]["message"]))[:1011]+'```', inline=False)
            e.add_field(name="Roles", value='```json\n' + str(inviteList[io].get("roles", None))[:1011]+'```', inline=False)
            await ctx.send(embed=e)
          except Exception as err:
            logger.error("Error:", err)
            e = discord.Embed(color=(await ctx.embed_colour()), title=io, description="Data error:\n"+str(inviteList[io]))
            await ctx.send(embed=e)
        return

    @hhinv.command(name="test")
    async def hhinvtest(self, ctx):
        "Test all invite-based welcomes"
        await ctx.send("Starting test....")
        userGuild = ctx.guild
        userObj = ctx.author
        # Fetch current custom invites only if exists
        savedInvites = await self.config.guild(userGuild).inviteList()
        if len(savedInvites) > 0:
            guildInvites = await userGuild.invites()
            for gio in guildInvites:
                try:
                    if savedInvites[str(gio.code)] and gio.uses >= savedInvites[str(gio.code)]["uses"]:
                        await self.inviteUsesSetter(userGuild, str(gio.code), gio.uses)
                        invHook = SyncWebhook.from_url(savedInvites[str(gio.code)]["channel"])
                        await self.hellohookSender(invHook, userObj, savedInvites[str(gio.code)]["message"])
                        # End early if webhook exists and was sent successfully
                        # return
                except Exception as err:
                    logger.error("Error:", err)
                    pass
        await ctx.send("Ended test")

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

        # Fetch current custom invites only if exists
        savedInvites = await self.config.guild(userGuild).inviteList()
        if len(savedInvites) > 0:
            guildInvites = await userGuild.invites()
            for gio in guildInvites:
                try:
                    if savedInvites[str(gio.code)] and gio.uses > savedInvites[str(gio.code)]["uses"]:
                        await self.inviteUsesSetter(userGuild, str(gio.code), gio.uses)
                        # Add role invites before sending welcome embed
                        irRoles = json.loads(savedInvites[str(gio.code)].get("roles", '[]'))
                        if len(irRoles) > 0:
                            for iro in irRoles:
                                try:
                                    irAdd = userGuild.get_role(int(iro))
                                    await userObj.add_roles(irAdd, reason="Hellohook invite role "+str(gio.code))
                                except: # Silently skip if role not found
                                    pass
                        invHook = SyncWebhook.from_url(savedInvites[str(gio.code)]["channel"])
                        await self.hellohookSender(invHook, userObj, savedInvites[str(gio.code)]["message"])
                        # End early if webhook exists and was sent successfully
                        return
                except Exception as err:
                    logger.debug("Error:", err)
                    pass

        # Otherwise, use default welcome
        greetMessage = await self.config.guild(userGuild).greetMessage()
        if not greetMessage:
            updatev1data = await self.updatev1data(userObj.guild)
            if updatev1data == False:
                return
        greetWebhook = await self.config.guild(userGuild).greetWebhook()
        webhook = SyncWebhook.from_url(greetWebhook)
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
        webhook = SyncWebhook.from_url(leaveWebhook)
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
