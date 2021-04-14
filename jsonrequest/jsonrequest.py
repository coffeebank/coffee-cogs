from redbot.core import Config, commands, checks
from urllib.parse import urlparse
import asyncio
import requests
import json

class Jsonrequest(commands.Cog):
    """Send and receive a json request"""

    def __init__(self):
        self.config = Config.get_conf(self, identifier=806715409318936616)
        default_guild = {
            "allowedDomains": [],
        }
        self.config.register_guild(**default_guild)

    async def red_get_data_for_user(self, *, user_id: int):
        # this cog does not story any data
        return {}

    async def red_delete_data_for_user(self, *, requester, user_id: int) -> None:
        # this cog does not story any data
        pass


    # Utility Commands

    def checkDomain(self, array, url):
        if array == []:
            # Server domain whitelist disabled; approve all json requests
            return True
        elif url in array:
            # Server domain whitelist enabled; approve if urldomain is in allowedDomains
            return True
        else:
            # Domain not approved or error occured; stop here
            return False

    def makeJsonRequest(self, url):
        reqdata = requests.get(url).json()
        reqcontent = json.dumps(reqdata, sort_keys=True, indent=2, separators=(',', ': '))
        return reqcontent


    # Bot Commands
    
    @commands.guild_only()
    @commands.group(name="setjsonrequest", aliases=["setjsonreq", "setjreq"])
    @checks.mod()
    async def setjsonreq(self, ctx: commands.Context):
        """Change the configurations for [p]jsonrequest

        All configurations are server-based.
        
        By default, all domains are allowed. When you add a domain below, the settings switch to a whitelist model where only added domains will work."""
        if not ctx.invoked_subcommand:
            pass

    @setjsonreq.command(name="add")
    async def setjradd(self, ctx, domain):
        """Add an allowed domain to the list
        
        Format: api.sampleapis.com
        
        The bot will check the domain against [Python's urlparse of json requests](https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urlparse).
        """
        allowedDomains = await self.config.guild(ctx.guild).allowedDomains()
        allowedDomains.append(domain)
        await self.config.guild(ctx.guild).allowedDomains.set(allowedDomains)
        await ctx.message.add_reaction("✅")

    @setjsonreq.command(name="remove")
    async def setjrremove(self, ctx, domain):
        """Remove an allowed domain to the list"""
        allowedDomains = await self.config.guild(ctx.guild).allowedDomains()
        
        try:
            allowedDomains.remove(domain)
        except:
            await ctx.send("Something went wrong :( Check if you have the name right using `[p]setjsonrequest list`")
        else:
            await self.config.guild(ctx.guild).allowedDomains.set(allowedDomains)
            await ctx.message.add_reaction("✅")

    @setjsonreq.command(name="list")
    async def setjrlist(self, ctx):
        """List current settings"""
        allowedDomains = await self.config.guild(ctx.guild).allowedDomains()
        if allowedDomains == []:
            await ctx.send("All domains are currently allowed!")
        else:
            await ctx.send(
                "Allowed Domains:```json\n" + str([dom+"\n" for dom in allowedDomains]) + "```"
            )


    @commands.command(name="jsonrequest", aliases=["jsonreq", "jreq"])
    async def jsonreq(self, ctx, url):
        """Makes a json request"""

        allowedDomains = await self.config.guild(ctx.guild).allowedDomains()
        urldomain = urlparse(url).netloc

        # Domain validation
        if self.checkDomain(allowedDomains, urldomain) == False:
            return await ctx.send("Oops! This domain isn't approved on this server....")

        # Json request
        try:
            reqcontent = self.makeJsonRequest(url)
        except:
            return await ctx.send("Oops! An error occured with the request....")
        else:
            # Max 2000 character limit on messages
            await ctx.send("```json\n"+str(reqcontent[:1986])+"```")
