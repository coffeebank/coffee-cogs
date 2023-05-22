from .bartender import Bartender

async def setup(bot):
    await bot.add_cog(Bartender())
