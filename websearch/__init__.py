from .websearch import websearch


def setup(bot):
    bot.add_cog(websearch())
