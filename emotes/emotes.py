# from redbot.core import Config
from redbot.core import Config, commands, checks
import asyncio
import aiohttp
import discord
import requests
import time
import random

class emotes(commands.Cog):
    """Custom emote solution for non-nitro users"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=806715409318936616)
        default_global = {
            "emoteGoogleSheetId": "",
            "emotestore": []
        }
        self.config.register_global(**default_global)


    @commands.group()
    @checks.is_owner()
    async def setemote(self, ctx: commands.Context):
        """Change the configurations for Emotes cog
        
        To set Google Sheets API key, use the command **`[p]set api gsheets api_key,YOURKEYHERE`**"""
        if not ctx.invoked_subcommand:
            pass
    
    @setemote.command(name="gsheet")
    async def setegsheet(self, ctx, sheetId: str):
        """Set Google Sheet ID with the emote data"""
        await self.config.emoteGoogleSheetId.set(sheetId)
        await ctx.message.add_reaction("✅")

    @setemote.command(aliases=["eupdate"])
    async def update(self, ctx):
        """Pull updates from Emote Google Sheet"""
        await ctx.message.add_reaction("⏳")

        # Retrieve data from bot
        gsheets_data = await self.config.emoteGoogleSheetId()
        if gsheets_data == "":
            return await ctx.send("The Google Sheets with Emotes data has not been set.")
        gsheets_key = await self.bot.get_shared_api_tokens("gsheets")
        if gsheets_key.get("api_key") is None:
            return await ctx.send("The Google Sheets API key has not been set.")

        # Run REST api request to Google Sheets API
        url = "https://sheets.googleapis.com/v4/spreadsheets/"+gsheets_data+"?key="+gsheets_key.get("api_key")+"&includeGridData=True"
        sendreq = requests.get(url)
        reqtext = sendreq.json()
        emotearray = []

        for sheet in reqtext["sheets"]:
            for rowdata in sheet["data"][0]["rowData"]:
                try:
                    b = rowdata["values"][1]["formattedValue"] #name
                    c = rowdata["values"][2]["formattedValue"]+"&size=64&emote="+b #url
                except:
                    # Skip if the cell doesn't have name/url
                    pass
                else:
                    # Check if the emote is saved under "fav"
                    try:
                        a = rowdata["values"][0]["formattedValue"] #fav
                    except:
                        a = False
                    # Check if the emote has extra tags
                    try:
                        d = rowdata["values"][3]["formattedValue"] #tags
                    except:
                        d = ""
                    # Format for emotearray
                    b = b.lower()
                    emotearray.append([a, b, c, d])
        # Commit the changes
        await self.config.emotestore.set(emotearray)
        await ctx.message.add_reaction("✅")


    @commands.command(aliases=["esearch", "ee"])
    async def emotesearch(self, ctx, search):
        """Search for image-ized emote url"""
        emotestore = await self.config.emotestore()
        emoteresults = []
        for a in emotestore:
            # [1] is name, [3] is tags
            if search.lower() in a[1] or search.lower() in a[3]:
                emoteresults.append(a)

        # Prune search results to only 4
        try:
            emoteresults = emoteresults[:3]
        except:
            pass

        # Send embed for each result
        for b in emoteresults:
            e = discord.Embed(color=(await ctx.embed_colour()), description=b[2])
            # [1] is emote name
            e.set_author(name=b[1], url=b[2])
            # [2] is image url
            e.set_thumbnail(url=b[2])
            # [3] is tags
            if b[3] != "":
                e.set_footer(text="Tags: "+b[3])
            await ctx.send(embed=e)



