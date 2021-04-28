from .pinshare import Pinshare

def setup(bot):
    bot.add_cog(Pinshare(bot))
