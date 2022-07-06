# from redbot.core import Config
from redbot.core import Config, commands, checks
import discord

class Behavior(commands.Cog):
    """behavior"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=806715409318936616)
        default_guild = {
        }
        self.config.register_guild(**default_guild)


    @commands.command(aliases=["behaviour"])
    async def behavior(self, ctx, emoji: str, *, behaviorText: str):
        """Behavior detected"""
        return await ctx.send(f"🚨 🚨 🚨  {emoji} {behaviorText.upper()} BEHAVIOR DETECTED 🚨 🚨 🚨")

    @commands.command()
    async def behaviorcustom(self, ctx, alertEmoji: str, emoji: str, *, behaviorText: str):
        """Behavior detected"""
        return await ctx.send(f"{alertEmoji} {alertEmoji} {alertEmoji}  {emoji} {behaviorText.upper()} DETECTED {alertEmoji} {alertEmoji} {alertEmoji}")
