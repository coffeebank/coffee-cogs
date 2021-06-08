from redbot.core import Config, commands, checks
from redbot.cogs.admin import admin
import asyncio
import aiohttp
import discord
import re
import time
from redbot.core.utils.predicates import ReactionPredicate
from redbot.core.utils.menus import start_adding_reactions

class Quarantine(commands.Cog):
    """Quarantine a user"""

    def __init__(self):
        self.config = Config.get_conf(self, identifier=806715409318936616)
        default_guild = {
            "muterole": "",
            "report": ""
        }
        self.config.register_guild(**default_guild)

    # This cog does not store any End User Data
    async def red_get_data_for_user(self, *, user_id: int):
        return {}
    async def red_delete_data_for_user(self, *, requester, user_id: int) -> None:
        pass

    
    @commands.guild_only()
    @commands.group()
    async def setquar(self, ctx: commands.Context):
        """Change the configurations for [p]quar"""
        if not ctx.invoked_subcommand:
            pass

    @setquar.command(name="role")
    @checks.mod()
    async def setquarrole(self, ctx, role: discord.Role=None):
        """Set the quarantine role"""
        await self.config.guild(ctx.guild).muterole.set(role.id)
        await ctx.message.add_reaction("✅")

    @setquar.command(name="report")
    @checks.mod()
    async def setquarreport(self, ctx, channel: discord.TextChannel=""):
        """Send an embed with quarantine reason to a specified channel"""
        await self.config.guild(ctx.guild).report.set(channel.id)
        await ctx.message.add_reaction("✅")

    @setquar.command(name="list")
    @checks.mod()
    async def setquarlist(self, ctx):
        """List current settings"""
        await ctx.send(
            "muterole: " + str(await self.config.guild(ctx.guild).muterole()) +"\n"+
            "report: " + str(await self.config.guild(ctx.guild).report())
        )


    @commands.command()
    @checks.mod()
    async def quar(self, ctx, user: discord.Member=None, *, reason=""):
        """Quarantines a user (config in `[p]setquar`)"""
        if not user:
            await ctx.send("Could not find user")
        else:
            # Find the role in server
            muteroledata = await self.config.guild(ctx.guild).muterole()
            muterole = ctx.guild.get_role(muteroledata)

            # Replace all of a user's roles with just [muterole]
            try:
                await user.edit(roles=[muterole])
            except:
                await ctx.send("Be sure to set the muterole first using [p]setquar :)")
            else:
                await ctx.message.add_reaction("✅")

            # Send report to channel
            destinationdata = await self.config.guild(ctx.guild).report()
            if destinationdata == "":
                return
            else:
                e = discord.Embed(color=(await ctx.embed_colour()), description=reason)
                e.set_footer(text="Sent in #{}".format(ctx.channel))

                if user.avatar_url:
                    e.set_author(name="User Quarantined: {}".format(user.display_name), icon_url=user.avatar_url)
                else:
                    e.set_author(name=user.display_name)

                destination = ctx.guild.get_channel(destinationdata)
                await destination.send(user.mention, embed=e)


    @commands.command()
    @checks.mod()
    async def quarall(self, ctx, quarType: int=1, *, userSearchText: str):
        """Search for all usernames (not nicknames) that match a string and quarantine them
        
        Types:
        1 - Normal quarantine
        2 - Kick the users
        3 - Ban the users
        """
        def quarTypeText(quarTypeInt: int):
            if quarTypeInt == 1:
                return "muterole"
            elif quarTypeInt == 2:
                return "kick"
            elif quartypeInt == 3:
                return "ban"
            else:
                return None

        try:
            userSearchRegex = re.compile(userSearchText, re.I)
        except re.error:
            return await ctx.send("Invalid search string. Format your search using Regex here and try again: https://pythex.org/")
        else:
            # Find the role in server
            muteroledata = await self.config.guild(ctx.guild).muterole()
            if muteroledata == "":
                return await ctx.send("Be sure to set the muterole first using `setquar` :')")
            muterole = ctx.guild.get_role(muteroledata)

            # Regex search display names and usernames
            # Only add users who aren't muted already
            memberObj = ctx.guild.members
            matches = []
            alreadyHave = 0
            for memObj in memberObj:
                searchText = str(memObj.display_name)+" "+str(memObj.name)
                if re.search(userSearchRegex, searchText):
                    if muterole not in memObj.roles:
                        matches.append(memObj)
                    else:
                        alreadyHave += 1

            # Return results in an embed asking if confirm
            desc = "Are you sure you want to {} the following users?\n\n".format(quarTypeText(quarType))
            userlist = ""
            for user in matches:
                userlist += user.mention + " " + str(user.id) + "\n"
            desc += userlist
            e = discord.Embed(color=(await ctx.embed_colour()), title="Quarantine Search Results", description=desc)
            if alreadyHave > 0:
                e.set_footer(text=str(alreadyHave)+" user(s) were already quarantined and skipped.")
            confirmEmbed = await ctx.send(embed=e)

            # Wait for confirm
            start_adding_reactions(confirmEmbed, ReactionPredicate.YES_OR_NO_EMOJIS)
            pred = ReactionPredicate.yes_or_no(confirmEmbed, ctx.author)
            try:
                await ctx.bot.wait_for("reaction_add", check=pred, timeout=60)
            except asyncio.TimeoutError:
                return await ctx.send("Selection timed out.")

            if pred.result is True:
                # User responded with tick
                await confirmEmbed.add_reaction("⏳")
                print("muterole: "+str(muterole))
                try:
                    if quarType == 1:
                        for quarUser in matches:
                            print("Quarantine type 1/muterole against "+str(quarUser.display_name))
                            await quarUser.edit(roles=[muterole])
                    elif quarType == 2:
                        for quarUser in matches:
                            print("Quarantine type 2/kick against "+str(quarUser.display_name))
                            await ctx.guild.kick(quarUser)
                    elif quarType == 3:
                        for quarUser in matches:
                            print("Quarantine type 3/ban against "+str(quarUser.display_name))
                            await ctx.guild.ban(quarUser)
                except:
                    return await ctx.send("Please confirm that I have permissions to manage members + manage roles....")
                else:
                    await confirmEmbed.add_reaction("💯")

                # Send report to channel
                destinationdata = await self.config.guild(ctx.guild).report()
                if destinationdata == "":
                    return
                else:
                    e2 = discord.Embed(color=(await ctx.embed_colour()), title="Quarantined: "+quarTypeText(quarType), description=userlist)
                    e2.set_footer(text="Sent in #{}".format(ctx.channel))
                    destination = ctx.guild.get_channel(destinationdata)
                    await destination.send(embed=e2)
            else:
                # User responded with cross
                return await ctx.send("Exited quarantine")
            