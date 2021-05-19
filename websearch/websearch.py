from redbot.core import Config, commands, checks
from redbot.cogs.admin import admin
import asyncio
import aiohttp
import discord
from urllib.parse import quote
import json

class Websearch(commands.Cog):
    """Gives you links to common search engines based on a search query."""

    def __init__(self):
        self.config = Config.get_conf(self, identifier=806715409318936616)
        default_guild = {
            "searchEngines": [
                {
                    "title": "Google",
                    "url": "https://www.google.com/search?hl=en&q="
                },
                {
                    "title": "Bing",
                    "url": "https://www.bing.com/search?q="
                },
                {
                    "title": "Ecosia",
                    "url": "https://www.ecosia.org/search?q="
                },
                {
                    "title": "DuckDuckGo",
                    "url": "https://duckduckgo.com/?t=ffab&q="
                },
            ]
        }
        self.config.register_guild(**default_guild)

    # This cog does not store any End User Data
    async def red_get_data_for_user(self, *, user_id: int):
        return {}
    async def red_delete_data_for_user(self, *, requester, user_id: int) -> None:
        pass

    @commands.command()
    async def websearch(self, ctx, *, searchtext):
        """Do a search"""
        query = quote(searchtext)
        searchEngines = await self.config.guild(ctx.guild).searchEngines()
        message = ""

        for k in searchEngines:
            # <url> to remove embeds
            # parse %s if it exists, else don't bother with it
            try:
                message = message + "\n" + str(k["title"]) + ": <" + str(k["url"].split('%s')[0]) + query + str(k["url"].split('%s')[1]) + ">"
            except:
                message = message + "\n" + str(k["title"]) + ": <" + str(k["url"]) + query + ">"
            
        await ctx.send(message)

    
    @commands.command()
    async def weblink(self, ctx, searchEngine, *, searchtext):
        """Do a search, with only a specific saved search engine"""
        query = quote(searchtext)
        searchEngines = await self.config.guild(ctx.guild).searchEngines()
        
        try:
            searchEn = next(item for item in searchEngines if item["title"] == searchEngine)
        except:
            # Try with a capitalization of searchEngine
            try:
                searchEn = next(item for item in searchEngines if item["title"] == str(searchEngine.capitalize()))
            except:
                await ctx.send("Oops, the search engine you listed couldn't be found. Check if you spelled it right using `[p]setwebsearch list`")

        # If searchEn was successfully defined above, then commence
        try:
            searchEn
        except:
            pass
        else:
            try:
                message = str(searchEn["url"].split('%s')[0]) + query + str(searchEn["url"].split('%s')[1])
            except:
                message = str(searchEn["url"]) + query
            finally:
                await ctx.send(message)



    @commands.guild_only()
    @commands.group()
    @checks.admin_or_permissions(manage_guild=True)
    async def setwebsearch(self, ctx: commands.Context):
        """Change the list of search engines"""
        if not ctx.invoked_subcommand:
            pass
    
    @setwebsearch.command(name="add")
    async def swebadd(self, ctx, searchName, *, searchUrl):
        """Add a new search engine
        
        By default, search queries will be added to the end of the url.
        You can also add "%s" in the url where you want the search query to go.
        """
        searchEngines = await self.config.guild(ctx.guild).searchEngines()
        searchEngines.append({"title": searchName, "url": searchUrl})
        await self.config.guild(ctx.guild).searchEngines.set(searchEngines)
        await ctx.message.add_reaction("✅")

    @setwebsearch.command(name="remove")
    async def swebremove(self, ctx, searchName):
        """Remove a search engine"""
        searchEngines = await self.config.guild(ctx.guild).searchEngines()
        
        try:
            itemToRemove = next(item for item in searchEngines if item["title"] == searchName)
            searchEngines.remove(itemToRemove)
        except:
            await ctx.send("Something went wrong :( Check if you have the name right using [p]setwebsearch list")
        else:
            await self.config.guild(ctx.guild).searchEngines.set(searchEngines)
            await ctx.message.add_reaction("✅")

    @setwebsearch.command(name="list")
    async def sweblist(self, ctx):
        """List all saved search engines"""
        searchEngines = await self.config.guild(ctx.guild).searchEngines()
        searchEnData = json.dumps(searchEngines, sort_keys=True, indent=2, separators=(',', ': '))
        await ctx.send("```json\n"+searchEnData+"```")
