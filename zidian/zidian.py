import asyncio
import io
import re
import zipfile

from redbot.core import Config, commands
import discord
import aiohttp

import logging
logger = logging.getLogger(__name__)


class Zidian(commands.Cog):
    """Chinese dictionary bot
    
    Sources:
    [CC-CEDICT](https://cc-cedict.org/wiki/) (License: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/))
    """

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=806715409318936616)

        # Bot owner configs
        default_global = {
            "dictHeaders": {
                "cedict": None,
            },
            "dictStorage": {
                "cedict": None,
            }
        }
        self.config.register_global(**default_global)

        # Server owner configs
        default_guild = {
        }
        self.config.register_guild(**default_guild)

    # This cog does not store any End User Data
    async def red_get_data_for_user(self, *, user_id: int):
        return {}
    async def red_delete_data_for_user(self, *, requester, user_id: int) -> None:
        pass


    ## Utility commands

    async def friendlyReact(ctx, react: str="✅", react_str: str="Done ✅"):
        try:
            return await ctx.message.add_reaction(react)
        except Exception:
            # discord.Forbidden - Missing add_reactions permission, send as plaintext message
            # discord.HybridCommandError - Slash command ctx message issue, just send as new message
            # discord.HTTPException - Original message deleted
            if react_str is not None:
                return await ctx.send(react_str)
            else:
                pass

    def search_file(self, filename, pattern):
        regex = re.compile(pattern, re.IGNORECASE)
        with open(filename, encoding="utf-8") as file:
            return [line.strip() for line in file if regex.search(line)]

    def stringize(self, arr):
        msg = ""
        for i in arr:
            msg += str(i) + "\n"
        return msg

    
    ## Bot commands

    @commands.group(aliases=["setzd"])
    async def setzidian(self, ctx: commands.Context):
        """Zidian cog settings
        
        Please run update command to initialize the dictionaries."""
        if not ctx.invoked_subcommand:
            pass

    @setzidian.command(name="list", aliases=["dict", "dictionaries"])
    @commands.is_owner()
    async def dictionaries(self, ctx):
        """List dictionaries"""
        srcHeaders = await self.config.dictHeaders()
        try:
            for i in srcHeaders:
                e = discord.Embed(color=(await ctx.embed_colour()), title=i, description=self.stringize(srcHeaders[i]).replace("#", ".")[:4096])
                await ctx.send(embed=e)
        except Exception as err:
            logger.error(err, exc_info=True)
            return await ctx.send("No dictionaries. Please run update command to initialize the dictionaries.")

    @setzidian.command(name="update")
    @commands.is_owner()
    async def update(self, ctx):
        """Update dictionaries"""

        ## cedict
        await self.config.dictStorage.cedict.set(None)
        url = "https://www.mdbg.net/chinese/export/cedict/cedict_1_0_ts_utf-8_mdbg.zip"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                content = await response.read()
                with zipfile.ZipFile(io.BytesIO(content)) as zip_file:
                    # Extract the first file in the zip (assumed to be the text file)
                    text_filename = zip_file.namelist()[0]
                    text_extracted = zip_file.extract(text_filename)
                    await self.config.dictStorage.cedict.set(text_extracted)
                    # Add source headers
                    cedictHeaders = self.search_file(text_extracted, r"^\#[\!]?\s.*")
                    await self.config.dictHeaders.cedict.set(cedictHeaders)

        await friendlyReact(ctx, "✅", "Done ✅")

    @commands.command(name="zidian")
    async def zidian(self, ctx, *, keyword):
        """Search the zidian 字典

        `咖啡`
        Chinese characters
        
        `ka fei` / `ka1 fei1`
        Pinyin - put spaces in between, tones optional, ü -> u:

        `coffee`
        English - Note: may not work well

        Note: CC-CEDICT does not contain use frequency, so some results may not be great.
        Settings: **`[p]setzidian`**
        """
        dictCedict = await self.config.dictStorage.cedict()


        assert dictCedict is not None
        
        patternKeyword = re.escape(keyword).replace(" ", r"s{0}(\s|\d\s)")
        startText = fr'(^{patternKeyword}|^[^\[]+\s{patternKeyword}|^[^\[]+\[{patternKeyword}(\d\]|\]).*|^[^\/]+\/{patternKeyword}([^=a-zA-Z]+).*)'
        middleText = fr'(^.*{patternKeyword}.*)'
        matches = None

        try:
            with open(dictCedict, encoding="utf-8") as file:
                matches = self.search_file(dictCedict, startText)
                sendEmbed = discord.Embed(color=(await ctx.embed_colour()), title="Results")
        except FileNotFoundError as err:
            return await ctx.send("Dictionary not initialized! Please run  **`[p]setzidian update`**  to initialize the dictionary first....")

        if len(matches) < 1:
            with open(dictCedict, encoding="utf-8") as file:
                matches = self.search_file(dictCedict, middleText)
                sendEmbed = discord.Embed(color=(await ctx.embed_colour()), title="Results (Extended)")

        if matches is not None:
            for index, i in enumerate(matches):
                if index == 6:
                    break
                entry = i.split("/", 1)
                try:
                    sendEmbed.add_field(name=entry[0], value=entry[1][:-1][:1100], inline=True)
                except:
                    pass

        await ctx.send(embed=sendEmbed)
