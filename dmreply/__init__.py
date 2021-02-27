from .dmreply import dmreply


def setup(bot):
    bot.add_cog(dmreply(bot))
