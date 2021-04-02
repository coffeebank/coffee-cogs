from .emotes import emotes


def setup(bot):
    bot.add_cog(emotes(bot))
