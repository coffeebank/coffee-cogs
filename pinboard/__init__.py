from .pinboard import Pinboard

def setup(bot):
    bot.add_cog(Pinboard(bot))
