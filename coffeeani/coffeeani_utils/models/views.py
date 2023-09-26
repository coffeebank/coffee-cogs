from redbot.core.commands import Context
from redbot.core.utils.views import SimpleMenu
import discord

class ExtendedSimpleMenu(SimpleMenu):
    """A simple Button menu, extended."""

    async def replace(self, ctx: Context, msg: discord.Message, *, ephemeral: bool = False):
        """
        Used to replace the menu displaying the first page requested.

        Parameters
        ----------
            ctx: `commands.Context`
                The context to start the menu in.
            msg: `discord.Message`
                A message object to edit.
        """
        self.author = ctx.author
        self.ctx = ctx
        kwargs = await self.get_page(self.current_page)
        self.message = await msg.edit(**kwargs)
        return self.message
