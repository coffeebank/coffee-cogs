from .quarantine import quarantine


def setup(bot):
    bot.add_cog(quarantine())
