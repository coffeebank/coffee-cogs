from .emotes import Emotes

def setup(bot):
    bot.add_cog(Emotes(bot))
