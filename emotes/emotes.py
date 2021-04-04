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


    # Utility Commands

    def convertNum(self, n):
        numarray = {2: '2️⃣', 3: '3️⃣', 4: '4️⃣', 5: '5️⃣', 6: '6️⃣', 7: '7️⃣', 8: '8️⃣', 9: '9️⃣'}
        try:
            return numarray[n]
        except:
            return "🔢"
            

    # Bot Commands

    @commands.group(aliases=["se"])
    @checks.is_owner()
    async def setemote(self, ctx: commands.Context):
        """Change the configurations for Emotes cog
        
        To set Google Sheets API key, use the command **`[p]set api gsheets api_key,YOURKEYHERE`**"""
        if not ctx.invoked_subcommand:
            pass
    
    @setemote.command(name="sheet")
    async def setesheet(self, ctx, sheetId: str):
        """Set Emote Google Sheet's ID, where the emote data was entered into"""
        await self.config.emoteGoogleSheetId.set(sheetId)
        await ctx.message.add_reaction("✅")

    @setemote.command(name="update")
    async def seteupdate(self, ctx):
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
    async def emotesearch(self, ctx, search, page: int=1):
        """Search for image-ized emote url"""
        emotestore = await self.config.emotestore()
        emoteresults = []
        for a in emotestore:
            # [1] is name, [3] is tags
            if search.lower() in a[1] or search.lower() in a[3]:
                emoteresults.append(a)

        # Exit early if empty
        if len(emoteresults) <= 0:
            return await ctx.message.add_reaction("💨")

        # If page=0, return all; otherwise, limit to 3 per page
        if page != 0:
            # Prune search results to only maxresults
            maxresults = 3
            if len(emoteresults) > maxresults:
                emotestart = page*maxresults-maxresults
                # Fallback to page 1 if specified page doesn't exist
                if emotestart > len(emoteresults):
                    page = 1
                    emotestart = (page-1)*maxresults
                emoteend = page*maxresults
                try:
                    emoteresults = emoteresults[emotestart:emoteend]
                except:
                    emoteresults = emoteresults[emotestart:]

        # Send react if it's not page 1 results
        if page != 1:
            await ctx.message.add_reaction(self.convertNum(page))

        # Send embed for each result
        for b in emoteresults:
            desc = f"`{b[2]}`"
            e = discord.Embed(color=(await ctx.embed_colour()), description=desc)
            # [1] is emote name
            e.set_author(name=b[1], url=b[2])
            # [2] is image url
            e.set_thumbnail(url=b[2])
            # [3] is tags
            if b[3] != "":
                e.set_footer(text="Tags: "+b[3])
            await ctx.send(embed=e)


    @commands.command(aliases=["esend", "eee"])
    async def emotesend(self, ctx, search):
        """Send an image-ized emote url, with first search result"""
        emotestore = await self.config.emotestore()
        for a in emotestore:
            # [1] is name, [3] is tags
            if search.lower() in a[1] or search.lower() in a[3]:
                # [2] is image url
                await ctx.send(a[2])
                # (try to) Delete trigger message
                try:
                    return await ctx.message.delete()
                except:
                    return



