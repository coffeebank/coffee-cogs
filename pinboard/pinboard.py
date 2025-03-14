from redbot.core import Config, commands
import discord
import json

import logging
logger = logging.getLogger(__name__)


class Pinboard(commands.Cog):
    """Make a communal notes board! Users can add and remove their contributions to a pinned message at any time, like adding sticky notes to an office board."""

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
        return {}
    async def red_delete_data_for_user(self, *, requester, user_id: int) -> None:
        pass


    # Utility Commands

    async def getMessageFromId(self, ctx, channelId: int, messageId: int):
        channelObj = ctx.guild.get_channel(channelId)
        return await channelObj.fetch_message(messageId)

    async def psAddData(self, ctx, pinnedMsgName, userId: int, data):
        pinStore = await self.config.guild(ctx.guild).pinStore()
        # Field value length max. 1024 characters
        if len(data) > 1024:
            raise commands.UserInputError("Error: Contents too long... Max 1024 characters.")

        pinStore[pinnedMsgName]["content"][str(userId)] = str(data)
        try:
            await self.config.guild(ctx.guild).pinStore.set(pinStore)
            return True
        except Exception as err:
            logger.error(err)
            return err

    async def psRemoveData(self, ctx, pinnedMsgName, userId: int):
        pinStore = await self.config.guild(ctx.guild).pinStore()
        pinStore[pinnedMsgName]["content"].pop(str(userId), None)
        try:
            await self.config.guild(ctx.guild).pinStore.set(pinStore)
            return True
        except keyError:
            raise KeyError
        except Exception as err:
            logger.error(err)
            raise err

    async def psUpdateData(self, ctx, pinnedMsgName, repin: bool=False):
        pinStore = await self.config.guild(ctx.guild).pinStore()
        pinnedMsgObj = await self.getMessageFromId(ctx, int(pinStore[pinnedMsgName]["channelId"]), int(pinStore[pinnedMsgName]["messageId"]))

        description = str(pinStore[pinnedMsgName]["description"])+"\u000a\u200b"

        # Embed title max. 256 characters
        if len(pinnedMsgName) > 256:
            raise commands.CommandError("Error: Pinboard label is too long... Server admin(s) can update this pinboard to fix this issue.")
        # Embed description max. 4096 characters
        if len(description) > 4096:
            raise commands.CommandError("Error: Description is too long... Server admin(s) can update this pinboard to fix this issue.")
        # Field count max. 25
        if len(pinStore[pinnedMsgName]["content"].items()) > 25:
            raise commands.UserInputError("Error: Sorry, the pinboard is full... Max 25 users total.")
        total_len = len(pinnedMsgName)+len(description)

        e = discord.Embed(color=(await ctx.embed_colour()), title=pinnedMsgName, description=description)

        for key, value in pinStore[pinnedMsgName]["content"].items():
            userObj = ctx.guild.get_member(int(key))
            if userObj is None:
                userObj = {
                    "display_name": int(key)[-4:]
                }
            payload = str(value)+"\u000a\u200b"

            # Field name length max. 256 characters
            if len(userObj.display_name) > 256:
                raise commands.UserInputError("Error: User display name too long... Max 256 characters.")
            # Field value length max. 1024 characters
            if len(payload) > 1024:
                raise commands.UserInputError("Error: Contents too long... Max 1024 characters.")
            # Total length max. 6000 characters
            total_len += len(userObj.display_name)
            total_len += len(payload)
            if total_len > 6000:
                raise commands.UserInputError("Error: Sorry, the pinboard is full... Max 6000 characters total.")

            e.add_field(name=userObj.display_name, value=payload, inline=True)

        try:
            await pinnedMsgObj.edit(embed=e)
        except Exception as err:
            logger.error(err)
            raise err

        if repin == True:
            await pinnedMsgObj.unpin()
            await pinnedMsgObj.pin()
        return

    async def psUpdateAll(self, ctx, repin=False):
        pinStore = await self.config.guild(ctx.guild).pinStore()
        errs = []
        for key, value in pinStore.items():
            try:
                await self.psUpdateData(ctx, key, repin)
            except Exception as err:
                logger.error(err)
                errs.append(err)
                # Log the error, and continue refreshing the others
                pass
        return errs


    # Bot Commands

    @commands.guild_only()
    @commands.group()
    async def pinboard(self, ctx: commands.Context):
        """Add your info to an active pinboard

        Make a communal notes board! Users can add and remove their contributions to a pinned message at any time, like adding sticky notes to an office board.

        Users can add their own contents to the pinboard, using the pinboard label (title).

        *Server admins: set up using **`[p]setpinboard`***        
        """
        if not ctx.invoked_subcommand:
            pass

    @pinboard.command(name="add", aliases=["edit"])
    @commands.bot_has_permissions(add_reactions=True)
    async def psadd(self, ctx, label: str, *, content: str):
        """Add/edit your info in a pinboard

        Note: Multi-word pinboard labels must be in **"quotes"**
        
        Note: Restrictions may apply for message contents, length, and update frequency."""
        try:
            await self.psAddData(ctx, label, ctx.message.author.id, content)
            await self.psUpdateData(ctx, label, repin=False)
        except commands.UserInputError as err:
            return await ctx.send(err)
        except Exception as err:
            await ctx.send("Error: Please see bot logs for details...")
        else:
            await ctx.message.add_reaction("✅")

    @pinboard.command(name="remove")
    @commands.bot_has_permissions(add_reactions=True)
    async def psremove(self, ctx, label: str):
        """Remove your own content from a pinboard"""
        try:
            await self.psRemoveData(ctx, label, ctx.message.author.id)
            await self.psUpdateData(ctx, label, repin=False)
        except KeyError:
            await ctx.send("Error: Couldn't find the pinboard. Did you enter the pinboard label correctly?")
        except commands.UserInputError as err:
            return await ctx.send(err)
        except Exception as err:
            await ctx.send("Error: Please see bot logs for details...")
        else:
            await ctx.message.add_reaction("✅")


    @commands.guild_only()
    @commands.group()
    @commands.has_permissions(manage_guild=True)
    async def setpinboard(self, ctx: commands.Context):
        """Create new pinboard messages

        Make a communal notes board! Users can add and remove their contributions to a pinned message at any time, like adding sticky notes to an office board.

        Pinboards have a label (title) and description. Users can add their own contents to the pinboard, using the pinboard label (title).
        
        Limits:
        - The pinboard label (title) is limited to 256 characters
        - The description is limited to 4096 characters
        - There can be up to 25 fields (users per pinboard)
        - A field's name (user display name) is limited to 256 characters
        - A field's value (user input data) is limited to 1024 characters
        - The sum of all characters in a message is limited to 6000 characters
        """
        if not ctx.invoked_subcommand:
            pass
    
    @setpinboard.command(name="add")
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(embed_links=True, add_reactions=True, manage_messages=True)
    async def spsadd(self, ctx, label: str, channel: discord.TextChannel, *, messageDescription: str):
        """Create a new pinboard
        
        Choose a label for the pinboard, so that you/others can easily refer back to it later. It will appear in the embed title.

        Note: Multi-word labels will need to be in **"quotes"** (even for users who want to add to it).
        """
        pinStore = await self.config.guild(ctx.guild).pinStore()
        # Check if label already exists
        if pinStore.get(label, None):
            return await ctx.send("Error: Label already exists... If you'd like to edit, please use the edit command instead.")

        await ctx.message.add_reaction("⏳")
        e = discord.Embed(color=(await ctx.embed_colour()), description="Pin me!")
        messageObj = await channel.send(embed=e)

        pinStore = await self.config.guild(ctx.guild).pinStore()
        pinStore[label] = {}
        pinStore[label]["channelId"] = channel.id
        pinStore[label]["messageId"] = messageObj.id
        pinStore[label]["description"] = messageDescription
        pinStore[label]["content"] = {}
        await self.config.guild(ctx.guild).pinStore.set(pinStore)

        try:
            await self.psUpdateData(ctx, label, True)
        except commands.UserInputError as err:
            return await ctx.send(err)
        except Exception as err:
            await ctx.send("Error: Please see bot logs for details...")
        else:
            await ctx.message.add_reaction("✅")
    
    @setpinboard.command(name="remove")
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(add_reactions=True)
    async def spsremove(self, ctx, label: str):
        """Remove a pinboard
        
        The message stays behind, but it will be removed from the tracking system, so it can't be updated anymore.
        
        ⚠️ This is irreversible."""
        pinStore = await self.config.guild(ctx.guild).pinStore()
        try:
            pinStore.pop(label, None)
        except KeyError:
            await ctx.send("Error: Couldn't find the pinboard. Did you enter the pinboard label correctly?")
        else:
            await ctx.message.add_reaction("✅")

    @setpinboard.command(name="edit")
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(embed_links=True, add_reactions=True)
    async def spsedit(self, ctx, label: str, *, description: str):
        """Edit description of a pinboard"""
        pinStore = await self.config.guild(ctx.guild).pinStore()
        pinStore[label]["description"] = description
        await self.config.guild(ctx.guild).pinStore.set(pinStore)
        try:
            await self.psUpdateData(ctx, label, repin=False)
        except commands.UserInputError as err:
            return await ctx.send(err)
        except Exception as err:
            return await ctx.send("Error: Please see bot logs...")
        else:
            await ctx.message.add_reaction("✅")

    @setpinboard.command(name="list", aliases=["export"])
    @commands.has_permissions(manage_guild=True)
    async def spslist(self, ctx):
        """List all pinboards
        
        TODO: Add support for >2000 characters
        """
        pinStore = await self.config.guild(ctx.guild).pinStore()
        pinStoreData = json.dumps(pinStore, sort_keys=True, indent=2, separators=(',', ': '))
        await ctx.send("```json\n"+pinStoreData[:1980]+"```")

    @setpinboard.command(name="import", hidden=True)
    @commands.has_permissions(administrator=True)
    async def spsimport(self, ctx, *, data: str):
        """Import data
        
        Import existing data, exported from **[p]setpinboard list`**"""
        await self.config.guild(ctx.guild).pinStore.set(json.loads(data))
        await ctx.send("done")

    @setpinboard.command(name="update")
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(embed_links=True, add_reactions=True, manage_messages=True)
    async def spsupdate(self, ctx, label: str, updateAll=False, repin=False):
        """Update one or all pinboards
        
        To update one pinboard, run **`[p]setpinboard update LABELNAMEHERE`**

        To update all, run **`[p]setpinboard update 0 True`**
        """
        if label in ["0", 0, None]:
            errs = await self.psUpdateAll(ctx, repin)
            if len(errs) > 0:
                await ctx.send("Completed with "+str(len(errs))+" errors:\n"+"\n".join([str(err) for err in errs])[:1950])
            else:
                await ctx.message.add_reaction("✅")
        else:
            try:
                await self.psUpdateData(ctx, label, repin)
            except commands.UserInputError as err:
                return await ctx.send(err)
            except Exception as err:
                return await ctx.send("Error: Please see bot logs...")
            else:
                await ctx.message.add_reaction("✅")

    @setpinboard.command(name="reset")
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(add_reactions=True)
    async def spsreset(self, ctx, areYouSure):
        """⚠️ Remove all pinboards tracked in the system
        
        Type **`[p]setpinboard reset True`** if you're really sure.
        
        **Note: This does not delete any pinboard messages. It only removes the tracking in the bot system. You will not be able to edit the messages again.**
        """
        if areYouSure == True:
            await self.config.guild(ctx.guild).pinStore.set({})
            await ctx.message.add_reaction("✅")
