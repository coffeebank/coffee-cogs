import asyncio
import io
import os
import re
import zipfile

from redbot.core import Config, commands, data_manager
from redbot.core.utils.views import SimpleMenu
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

    async def friendlyReact(self, ctx, react: str="✅", react_str: str="Done ✅"):
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

    def group_array_items(self, arr: list, n: int):
        return [arr[i:i + n] for i in range(0, len(arr), n)]

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
    @commands.bot_has_permissions(embed_links=True)
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
        # Fetch latest version
        # To see current version saved in bot, use `[p]setzidian list`
        # Version and license info will be displayed
        url = "https://www.mdbg.net/chinese/export/cedict/cedict_1_0_ts_utf-8_mdbg.zip"
        await self.friendlyReact(ctx, "⏳", "Fetching ⏳")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        err = aiohttp.ClientResponseError(
                            response.request_info,
                            response.history,
                            status=response.status,
                            message=response.reason
                        )
                        logger.error(f"Failed to fetch: {str(err)}")
                        raise err
                    content = await response.read()
                    with zipfile.ZipFile(io.BytesIO(content)) as zip_file:
                        # Extract the first file in the zip (assumed to be the text file)
                        cog_data_path = None
                        try:
                            cog_data_path = str(data_manager.cog_data_path(cog_instance=self))
                            logger.info("Saved cedict to Red cog data path: " + cog_data_path)
                        except Exception as err:
                            # NameError: name 'redbot' is not defined
                            if err is not NameError:
                                logger.error(err, exc_info=True)
                            cog_data_path = os.path.dirname(os.path.abspath(__file__))
                            logger.info("Saved cedict to cog directory: " + cog_data_path)
                        text_filename = zip_file.namelist()[0]
                        full_path = os.path.join(cog_data_path, text_filename)
                        try:
                            with open(full_path, "wb") as extracted_file:
                                extracted_file.write(zip_file.read(text_filename))
                                await self.config.dictStorage.cedict.set(full_path)
                        except Exception as err:
                            logger.error(err, exc_info=True)
                            raise err
                        # Add source headers
                        cedictHeaders = self.search_file(full_path, r"^\#[\!]?\s.*")
                        await self.config.dictHeaders.cedict.set(cedictHeaders)
        except Exception as err:
            return await ctx.send("Error: "+str(err))
        else:
            await self.friendlyReact(ctx, "✅", "Done ✅")
        finally:
            await session.close()


    @commands.command(name="zidian")
    @commands.bot_has_permissions(embed_links=True)
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

        try:
            assert dictCedict is not None
        except AssertionError:
            return await ctx.send("Error: Please run `[p]setzidian update` to initialize the dictionary first!")

        await self.friendlyReact(ctx, "⏳", "Searching ⏳")
        
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

        extended_results = None
        if len(matches) < 1:
            with open(dictCedict, encoding="utf-8") as file:
                matches = self.search_file(dictCedict, middleText)
                extended_results = "(Extended)"

        if not matches:
            return await ctx.send("Sorry, no results found...")

        results = []
        for index, i in enumerate(matches):
            result = {}
            entry = i.split("/", 1)
            try:
                result["title"] = entry[0]
                result["description"] = entry[1][:-1][:1100]
            except Exception as err:
                logger.debug(err)
                pass
            results.append(result)
        
        results_grouped = self.group_array_items(results, 6)
        results_grouped_embeds = []
        for idx, group in enumerate(results_grouped):
            e = discord.Embed(
              color=(await self.bot.get_embed_colour(self))
            )
            for g_result in group:
                e.add_field(
                    name=g_result.get("title", "-"), 
                    value=g_result.get("description", "-"),
                    inline=True
                )
            e.set_footer(text=" ・ ".join(filter(None, ["Results by CC-CEDICT", str(idx+1)+"/"+str(len(results_grouped)), extended_results])))
            results_grouped_embeds.append(e)

        await SimpleMenu(pages=results_grouped_embeds, timeout=90).start(ctx)
        await self.friendlyReact(ctx, "✅", None)
