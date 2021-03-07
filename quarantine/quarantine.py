from redbot.core import Config, commands, checks
from redbot.cogs.admin import admin
import asyncio
import aiohttp
import discord
import time

class quarantine(commands.Cog):
    """Quarantine a user"""

    def __init__(self):
        self.config = Config.get_conf(self, identifier=806715409318936616)
        default_guild = {
            "muterole": "",
            "report": ""
        }
        self.config.register_guild(**default_guild)

    async def red_get_data_for_user(self, *, user_id: int):
        # this cog does not story any data
        return {}

    async def red_delete_data_for_user(self, *, requester, user_id: int) -> None:
        # this cog does not story any data
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
            finally:
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
