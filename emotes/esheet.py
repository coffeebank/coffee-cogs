import discord
import json
import asyncio
import aiohttp
import time

class EmoteSheet():
  """EmoteSheet is the engine behind integrating with the Google Sheets API to create a searchable emote database inside the bot."""

  def __init__(self, **kwargs):
      super().__init__()


  # General Utility Commands

  def convertNum(self, n):
      numarray = {2: '2️⃣', 3: '3️⃣', 4: '4️⃣', 5: '5️⃣', 6: '6️⃣', 7: '7️⃣', 8: '8️⃣', 9: '9️⃣'}
      try:
          return numarray[n]
      except:
          return "🔢"


  async def search(self, ctx, emotestore, search, page):
    emoteresults = []
    for a in emotestore:
      # [1] is name, [3] is tags
      if search.lower() in a[1] or search.lower() in a[3]:
        emoteresults.append(a)

    # Exit early if empty
    if len(emoteresults) <= 0:
      return await ctx.message.add_reaction("💨")

    # If page=0, return all; otherwise, limit to 3 per page
    if page == 0:
      emotelength = len(emoteresults)
      await ctx.send(f"{emotelength} results")
    else:
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
    if page > 1:
      await ctx.message.add_reaction(EmoteSheet.convertNum(self, page))

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
      # Ratelimit to 1 per 0.75s if bot is going to list all at once
      if page == 0:
        time.sleep(0.65)
      await ctx.send(embed=e)


  def searchsingle(self, search, emotestore):
    for a in emotestore:
      # [1] is name, [3] is tags
      if search.lower() in a[1] or search.lower() in a[3]:
        return a
    return False


  async def send(self, ctx, search, emotestore):
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


  async def update(self, ctx, bot, gsheets_data):
    # Retrieve data from bot
    if gsheets_data == "":
      return "The Google Sheets with Emotes data has not been set."
    gsheets_key = await bot.get_shared_api_tokens("gsheets")
    if gsheets_key.get("api_key") is None:
      return "The Google Sheets API key has not been set."

    # Run REST api request to Google Sheets API
    url = "https://sheets.googleapis.com/v4/spreadsheets/"+gsheets_data+"?key="+gsheets_key.get("api_key")+"&includeGridData=True"
    async with aiohttp.ClientSession() as session:
      async with session.get(url) as resp:
        # Loads whole json into memory, may consider improving in future
        # https://docs.aiohttp.org/en/stable/client_quickstart.html#streaming-response-content
        reqtext = await resp.json()
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

        return emotearray
