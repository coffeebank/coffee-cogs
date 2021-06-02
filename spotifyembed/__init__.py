from .spotifyembed import Spotifyembed
from redbot.core.utils import get_end_user_data_statement

__red_end_user_data_statement__  = get_end_user_data_statement(__file__)

def setup(bot):
    bot.add_cog(Spotifyembed(bot))
