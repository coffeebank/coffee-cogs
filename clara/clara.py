from redbot.core import Config, app_commands, commands, checks
import discord

class Clara(commands.Cog):
    """See info about the servers your bot is in.
    
    For bot owners only.
    """

    def __init__(self, bot):
        self.config = Config.get_conf(self, identifier=806715409318936616)
        self.bot = bot

    # This cog does not store any End User Data
    async def red_get_data_for_user(self, *, user_id: int):
        return {}
    async def red_delete_data_for_user(self, *, requester, user_id: int) -> None:
        pass


    @commands.hybrid_command(name="botguilds", aliases=["botservers"])
    @commands.is_owner()
    async def botguilds(self, ctx):
        """See info about the servers your bot is in.

        Lists total guilds, total approximate member count, and top large servers using your bot.

        The command may take a while to run.
        """
        await ctx.message.add_reaction("⏳")
        guilds = [guild async for guild in self.bot.fetch_guilds(limit=None)]
        guilds_sorted = sorted(guilds, key=lambda x: x.approximate_member_count, reverse=True)
        total_guild_count = len(guilds)
        total_member_count = 0
        send_body = "```"
        for guild in guilds_sorted:
            send_body += f"\n{guild.approximate_member_count} ({guild.approximate_presence_count}) - {guild.id} - {guild.name}"
            total_member_count += guild.approximate_member_count
        await ctx.message.clear_reaction("⏳")
        await ctx.send(f"Guilds: `{total_guild_count}`\nMembers: `{total_member_count}` total (active now)\n")
        send_body = send_body[:1990] + "\n```"
        return await ctx.send(send_body)
