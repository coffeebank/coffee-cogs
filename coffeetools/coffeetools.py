from redbot.core import Config, commands, checks
import discord
import random

class Coffeetools(commands.Cog):
    """Replacement for 'General' cog, since it needs to be disabled to override certain commands."""

    def __init__(self):
        self.config = Config.get_conf(self, identifier=806715409318936616)

    # This cog does not store any End User Data
    async def red_get_data_for_user(self, *, user_id: int):
        return {}
    async def red_delete_data_for_user(self, *, requester, user_id: int) -> None:
        pass

    @commands.command()
    @commands.has_permissions(embed_links=True)
    async def choose(self, ctx, *, choosetext):
        """Have the bot choose for you
        
        **`[p]choose item1 | item2 | item3`**"""
        # Split choosetext into an array, and return random choice
        choosearray = choosetext.split("|")
        # Wrap in an embed to prevent spam links, @mentions, etc. (Repo issue #5)
        e = discord.Embed(color=(await ctx.embed_colour()), description=random.choice(choosearray))
        e.set_footer(text="'choose' requested by "+ctx.author.display_name)
        # Catch error
        try:
            return await ctx.send(embed=e)
        except:
            return await ctx.send("Sorry, an error occurred. Are you using only alphanumeric characters?")
