from .sendhook import sendhook


def setup(bot):
    bot.add_cog(sendhook())
