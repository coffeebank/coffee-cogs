from .google import google


def setup(bot):
    bot.add_cog(google())
