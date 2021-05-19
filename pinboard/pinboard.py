from redbot.core import Config, commands, checks
from redbot.cogs.admin import admin
import asyncio
import aiohttp
import discord
from urllib.parse import quote
import json

class Pinboard(commands.Cog):
    """Make pinned messages communal! Users can add and remove their contributions to a pinned message at any time."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=806715409318936616)
        default_guild = {
            "pinStore": {}
        }
        """
        format:
        {
            "pinnedMsgName": {
                "channelId": int,
                "messageId": int,
                "description": "str",
                "content": {
                    "userId": "data",
                    "userId": "data"
                }
            },
            "pinnedMsgName": {
                "channelId": int,
                "messageId": int,
                "description": "str",
                "content": {
                    "userId": "data",
                    "userId": "data"
                }
            }
        }
        """
        self.config.register_guild(**default_guild)


    async def red_get_data_for_user(self, *, user_id: int):
        # this cog does not story any data
        return {}

    async def red_delete_data_for_user(self, *, requester, user_id: int) -> None:
        # this cog does not story any data
        pass


    # Utility Commands

    async def getMessageFromId(self, ctx, channelId: int, messageId: int):
        channelObj = ctx.guild.get_channel(channelId)
        return await channelObj.fetch_message(messageId)

    async def psAddData(self, ctx, pinnedMsgName, userId: int, data):
        pinStore = await self.config.guild(ctx.guild).pinStore()
        pinStore[pinnedMsgName]["content"][str(userId)] = str(data)
        try:
            await self.config.guild(ctx.guild).pinStore.set(pinStore)
            return True
        except:
            return False

    async def psRemoveData(self, ctx, pinnedMsgName, userId: int):
        pinStore = await self.config.guild(ctx.guild).pinStore()
        pinStore[pinnedMsgName]["content"].pop(str(userId), None)
        try:
            await self.config.guild(ctx.guild).pinStore.set(pinStore)
            return True
        except:
            return False

    async def psUpdateData(self, ctx, pinnedMsgName, repin: bool=False):
        pinStore = await self.config.guild(ctx.guild).pinStore()
        pinnedMsgObj = await self.getMessageFromId(ctx, int(pinStore[pinnedMsgName]["channelId"]), int(pinStore[pinnedMsgName]["messageId"]))

        description = str(pinStore[pinnedMsgName]["description"])+"\u000a\u200b"

        e = discord.Embed(color=(await ctx.embed_colour()), title=pinnedMsgName, description=description)

        for key, value in pinStore[pinnedMsgName]["content"].items():
            # userObj = self.bot.get_user(int(key))
            userObj = ctx.guild.get_member(int(key))
            payload = str(value)+"\u000a\u200b"
            e.add_field(name=userObj.display_name, value=payload, inline=True)

        await pinnedMsgObj.edit(embed=e)
        if repin == True:
            await pinnedMsgObj.unpin()
            await pinnedMsgObj.pin()
        return

        # description = str(pinStore[pinnedMsgName]["description"])
        # content = ""

        # for key, value in pinStore[pinnedMsgName]["content"].items():
        #     userObj = self.bot.get_user(int(key))
        #     content = content+userObj.mention+"\n"+str(value)+"\n\n"

        # msgbody = description+"\n\n"+content
        # await pinnedMsgObj.edit(content=msgbody)
        # if repin == True:
        #     await pinnedMsgObj.unpin()
        #     await pinnedMsgObj.pin()
        # return

    async def psUpdateAll(self, ctx, repin=False):
        pinStore = await self.config.guild(ctx.guild).pinStore()
        for key, value in pinStore.items():
            await self.psUpdateData(ctx, key, repin)
        return


    # Bot Commands

    @commands.guild_only()
    @commands.group()
    async def pinshare(self, ctx: commands.Context):
        """Change the list of active pinned messages"""
        if not ctx.invoked_subcommand:
            pass

    @pinshare.command(name="add", aliases=["edit"])
    async def psadd(self, ctx, pinnedMsgName, *, content):
        """Add or edit your own content to a pinned message"""
        await self.psAddData(ctx, pinnedMsgName, ctx.message.author.id, content)
        await self.psUpdateData(ctx, pinnedMsgName, repin=False)
        await ctx.message.add_reaction("✅")

    @pinshare.command(name="remove")
    async def psremove(self, ctx, pinnedMsgName):
        """Remove your own content to a pinned message"""
        await self.psRemoveData(ctx, pinnedMsgName, ctx.message.author.id)
        await ctx.message.add_reaction("✅")


    @commands.guild_only()
    @commands.group()
    @checks.admin_or_permissions(manage_guild=True)
    async def setpinshare(self, ctx: commands.Context):
        """Change the list of active pinned messages"""
        if not ctx.invoked_subcommand:
            pass
    
    @setpinshare.command(name="add")
    async def spsadd(self, ctx, pinnedMsgName, channel: discord.TextChannel, *, messageDescription):
        """Create a new pinned message
        
        pinnedMsgName is a label for the pinned message, so that you/others can easily refer back to it later. It should be a single word and short/easy to remember."""
        await ctx.message.add_reaction("⏳")
        e = discord.Embed(color=(await ctx.embed_colour()), description="Pin me!")
        messageObj = await channel.send(embed=e)

        pinStore = await self.config.guild(ctx.guild).pinStore()
        pinStore[pinnedMsgName] = {}
        pinStore[pinnedMsgName]["channelId"] = channel.id
        pinStore[pinnedMsgName]["messageId"] = messageObj.id
        pinStore[pinnedMsgName]["description"] = messageDescription
        pinStore[pinnedMsgName]["content"] = {}
        await self.config.guild(ctx.guild).pinStore.set(pinStore)

        await self.psUpdateData(ctx, pinnedMsgName, True)
        await ctx.message.add_reaction("✅")
    
    @setpinshare.command(name="remove")
    async def spsremove(self, ctx, pinnedMsgName):
        """Remove a pinned message
        
        The message stays behind, but it will be removed from the tracking system, so you can't update it anymore."""
        pinStore = await self.config.guild(ctx.guild).pinStore()
        pinStore.pop(pinnedMsgName, None)
        await ctx.message.add_reaction("✅")

    @setpinshare.command(name="edit")
    async def spsedit(self, ctx, pinnedMsgName, *, description):
        """Edit description of a pinned message"""
        pinStore = await self.config.guild(ctx.guild).pinStore()
        pinStore[pinnedMsgName]["description"] = description
        await self.config.guild(ctx.guild).pinStore.set(pinStore)
        await self.psUpdateData(ctx, pinnedMsgName)
        await ctx.message.add_reaction("✅")

    @setpinshare.command(name="export")
    async def spsexport(self, ctx):
        """Export data"""
        await ctx.send(str(await self.config.guild(ctx.guild).pinStore()))

    @setpinshare.command(name="import")
    async def spsimport(self, ctx, *, data):
        """Import data"""
        await self.config.guild(ctx.guild).pinStore().set(data)
        await ctx.send("done")

    @setpinshare.command(name="list")
    async def spslist(self, ctx):
        """List all pinned messages"""
        pinStore = await self.config.guild(ctx.guild).pinStore()
        pinStoreData = json.dumps(pinStore, sort_keys=True, indent=2, separators=(',', ': '))
        await ctx.send("```json\n"+pinStoreData+"```")

    @setpinshare.command(name="update")
    async def spsupdate(self, ctx, pinnedMsgName=None, repin=False):
        """Update one or all pinned messages"""
        if pinnedMsgName == None:
            await self.psUpdateAll(ctx, repin)
        else:
            await self.psUpdateData(ctx, pinnedMsgName, repin)
        await ctx.message.add_reaction("✅")

    @setpinshare.command(name="reset")
    async def spsreset(self, ctx, areYouSure=False):
        """⚠️ Reset all pinned messages
        
        Type **`[p]setpinshare reset True`** if you're really sure."""
        if areYouSure == True:
            await self.config.guild(ctx.guild).pinStore.set({})
            await ctx.message.add_reaction("✅")
