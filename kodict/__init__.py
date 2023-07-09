from .kodict import Kodict
try:
    # Red-DiscordBot
    from redbot.core.utils import get_end_user_data_statement
    __red_end_user_data_statement__  = get_end_user_data_statement(__file__)
except (ImportError, ModuleNotFoundError):
    # Discord.py
    pass

async def setup(bot):
    await bot.add_cog(Kodict(bot))
