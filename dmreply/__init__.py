from .dmreply import Dmreply

def setup(bot):
    bot.add_cog(Dmreply(bot))
