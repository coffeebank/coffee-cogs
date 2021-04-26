from .msgmover import Msgmover

def setup(bot):
    bot.add_cog(Msgmover(bot))
