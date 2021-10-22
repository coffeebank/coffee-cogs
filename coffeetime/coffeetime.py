import discord
import pytz
from datetime import datetime
from fuzzywuzzy import fuzz, process
from typing import Optional, Literal
from redbot.core import Config, commands
from redbot.core.utils.chat_formatting import pagify
from redbot.core.utils.menus import close_menu, menu, DEFAULT_CONTROLS


__version__ = "2.1.1"


class Coffeetime(commands.Cog):
    """Gets times across the world..."""
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, 278049241001, force_registration=True)
        default_user = {"usertime": None}
        self.config.register_user(**default_user)
        
    async def red_delete_data_for_user(
        self, *, requester: Literal["discord", "owner", "user", "user_strict"], user_id: int,
    ):
        await self.config.user_from_id(user_id).clear()

    async def get_usertime(self, user: discord.User):
        tz = None
        usertime = await self.config.user(user).usertime()
        if usertime:
            tz = pytz.timezone(usertime)

        return usertime, tz

    def fuzzy_timezone_search(self, tz: str):
        fuzzy_results = process.extract(tz.replace(" ", "_"), pytz.common_timezones, limit=500, scorer=fuzz.partial_ratio)
        matches = [x for x in fuzzy_results if x[1] > 98] 
        return matches

    async def format_results(self, ctx, tz):
        if not tz:
            await ctx.send(
                "Sorry, didn't find a timezone for your city :(\nTry another nearby city in your timezone, or finding your city in this full list:\nhttps://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List"
            )
            return None
        elif len(tz) == 1:
            # command specific response, so don't do anything here
            return tz
        else:
            msg = ""
            for timezone in tz:
                msg += f"{timezone[0]}\n"

            embed_list = []
            for page in pagify(msg, delims=["\n"], page_length=500):
                e = discord.Embed(title=f"{len(tz)} results... could you try being more specific?\n\n ie. `America/Los Angeles`", description=page)
                e.set_footer(text="https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List")
                embed_list.append(e)
            if len(embed_list) == 1:
                close_control = {"\N{CROSS MARK}": close_menu}
                await menu(ctx, embed_list, close_control)
            else:
                await menu(ctx, embed_list, DEFAULT_CONTROLS)
            return None


    # Bot Commands

    @commands.command()
    async def time(self, ctx, user: discord.Member = None):
        """Shows the current time for the specified user."""
        if not user:
            user = ctx.author
        usertime, tz = await self.get_usertime(user)
        if usertime:
            time = datetime.now(tz)
            fmt = "**%H:%M** *(%I:%M %p)*\n**%A, %d %B %Y**\n*%Z (UTC %z)*"
            time = time.strftime(fmt)

            timemsg1 = f"{user.display_name}'s current time is"
            timemsg2 = ""
            timemsg3 = f": \n>>> {str(time)}, *{usertime}*"
            timemsg4 = ""
            
            # Compare times
            if user != ctx.author:
                usertime, user_tz = await self.get_usertime(ctx.author)
                othertime, other_tz = await self.get_usertime(user)

                if usertime and othertime:
                    user_now = datetime.now(user_tz)
                    user_diff = user_now.utcoffset().total_seconds() / 60 / 60
                    other_now = datetime.now(other_tz)
                    other_diff = other_now.utcoffset().total_seconds() / 60 / 60
                    time_diff = abs(user_diff - other_diff)
                    time_diff_text = f"{time_diff:g}"
                    fmt = "**%H:%M %Z (UTC %z)**"
                    other_time = other_now.strftime(fmt)
                    plural = "" if time_diff_text == "1" else "s"
                    time_amt = "the same as yours" if time_diff_text == "0" else f"{time_diff_text} hour{plural}"
                    position = "ahead of" if user_diff < other_diff else "behind"
                    position_text = "" if time_diff_text == "0" else f" {position} you"

                    timemsg2 = f" **{time_amt}{position_text}**"
                else:
                  if not usertime:
                      timemsg4 = f"You haven't set your timezone yet 👀 Do `{ctx.prefix}timeset` to share your timezone!"

            await ctx.send(timemsg1+timemsg2+timemsg3)
            if timemsg4:
              await ctx.send(timemsg4)
        else:
            await ctx.send(f"{user.display_name} hasn't set a timezone yet. Set one by typing `{ctx.prefix}timeset` !")

    @commands.command()
    async def timeset(self, ctx, *, city_name_here):
        """
        Sets your timezone.

        Most big cities near you should work....

        Not working? [See the full list of cities here >](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List)
        """
        tz_results = self.fuzzy_timezone_search(city_name_here)
        tz_resp = await self.format_results(ctx, tz_results)
        if tz_resp:
            await self.config.user(ctx.author).usertime.set(tz_resp[0][0])
            await ctx.send(f"Successfully set your timezone to **{tz_resp[0][0]}**!")

    @commands.guild_only()
    @commands.group()
    async def timetools(self, ctx):
        """
        Checks the time.
        For the list of supported timezones, see here:
        https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
        """
        pass

    @timetools.command()
    async def tz(self, ctx, *, timezone_name: Optional[str] = None):
        """Gets the time in any timezone."""
        if timezone_name is None:
            time = datetime.now()
            fmt = "**%H:%M** %d-%B-%Y"
            await ctx.send(f"Current system time: {time.strftime(fmt)}")
        else:
            tz_results = self.fuzzy_timezone_search(timezone_name)
            tz_resp = await self.format_results(ctx, tz_results)
            if tz_resp:
                time = datetime.now(pytz.timezone(tz_resp[0][0]))
                fmt = "**%H:%M** %d-%B-%Y **%Z (UTC %z)**"
                await ctx.send(time.strftime(fmt))

    @timetools.command()
    async def iso(self, ctx, *, iso_code=None):
        """Looks up ISO3166 country codes and gives you a supported timezone."""
        if iso_code is None:
            await ctx.send("That doesn't look like a country code!")
        else:
            exist = True if iso_code.upper() in pytz.country_timezones else False
            if exist is True:
                tz = str(pytz.country_timezones(iso_code.upper()))
                msg = (
                    f"Supported timezones for **{iso_code.upper()}:**\n{tz[:-1][1:]}"
                    f"\n**Use** `{ctx.prefix}time tz Continent/City` **to display the current time in that timezone.**"
                )
                await ctx.send(msg)
            else:
                await ctx.send(
                    "That code isn't supported.\nFor a full list, see here: "
                    "<https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes>\n"
                    "Use the two-character code under the `Alpha-2 code` column."
                )

    @timetools.command()
    @commands.is_owner()
    async def set(self, ctx, user: discord.User, *, timezone_name=None):
        """
        Allows the bot owner to edit users' timezones.
        Use a user id for the user if they are not present in your server.
        """
        if not user:
            user = ctx.author
        if len(self.bot.users) == 1:
            return await ctx.send("This cog requires Discord's Privileged Gateway Intents to function properly.")
        if user not in self.bot.users:
            return await ctx.send("I can't see that person anywhere.")
        if timezone_name is None:
            return await ctx.send_help()
        else:
            tz_results = self.fuzzy_timezone_search(timezone_name)
            tz_resp = await self.format_results(ctx, tz_results)
            if tz_resp:
                await self.config.user(user).usertime.set(tz_resp[0][0])
                await ctx.send(f"Successfully set {user.name}'s timezone to **{tz_resp[0][0]}**.")

    @timetools.command()
    async def user(self, ctx, user: discord.Member = None):
        """Shows the current time for the specified user."""
        if not user:
            await ctx.send("That isn't a user!")
        else:
            usertime, tz = await self.get_usertime(user)
            if usertime:
                time = datetime.now(tz)
                fmt = "**%H:%M** %d-%B-%Y **%Z (UTC %z)**"
                time = time.strftime(fmt)
                await ctx.send(
                    f"{user.name}'s current timezone is: **{usertime}**\n" f"The current time is: {str(time)}"
                )
            else:
                await ctx.send("That user hasn't set their timezone.")

    @timetools.command()
    async def compare(self, ctx, user: discord.Member = None):
        """Compare your saved timezone with another user's timezone."""
        if not user:
            return await ctx.send_help()

        usertime, user_tz = await self.get_usertime(ctx.author)
        othertime, other_tz = await self.get_usertime(user)

        if not usertime:
            return await ctx.send(
                f"You haven't set your timezone. Do `{ctx.prefix}time me Continent/City`: "
                "see <https://en.wikipedia.org/wiki/List_of_tz_database_time_zones>"
            )
        if not othertime:
            return await ctx.send(f"That user's timezone isn't set yet.")

        user_now = datetime.now(user_tz)
        user_diff = user_now.utcoffset().total_seconds() / 60 / 60
        other_now = datetime.now(other_tz)
        other_diff = other_now.utcoffset().total_seconds() / 60 / 60
        time_diff = abs(user_diff - other_diff)
        time_diff_text = f"{time_diff:g}"
        fmt = "**%H:%M %Z (UTC %z)**"
        other_time = other_now.strftime(fmt)
        plural = "" if time_diff_text == "1" else "s"
        time_amt = "the same time zone as you" if time_diff_text == "0" else f"{time_diff_text} hour{plural}"
        position = "ahead of" if user_diff < other_diff else "behind"
        position_text = "" if time_diff_text == "0" else f" {position} you"

        await ctx.send(f"{user.display_name}'s time is {other_time} which is {time_amt}{position_text}.")
