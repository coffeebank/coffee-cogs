from .sendhook import Sendhook


def setup(bot):
    bot.add_cog(Sendhook())
