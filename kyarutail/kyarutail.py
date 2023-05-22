from redbot.core import Config, commands, checks
import asyncio
import aiohttp
import discord
from discord import Webhook, SyncWebhook
import random

class Kyarutail(commands.Cog):
    """Convert your messages into a message written with emotes of Kyaru's tail. Kyaru (aka. Karyl) is a character from Princess Connect! Re:Dive."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=806715409318936616)
        default_guild = {
            "kyaruEmotes": {
              "a": "892633805842702378",
              "b": "892633821672005673",
              "c": "892637383990837308",
              "d": "892637399056797697",
              "e": "892645977498988604",
              "f": "892645990799138847",
              "g": "892646008444579882",
              "h": "892646041223057439",
              "i": "895074318281748561",
              "j": "892646046403002429",
              "k": "892646047065706526",
              "l": "892646046444957716",
              "m": "892646046671466517",
              "n": "892646047166373888",
              "o": "895070743132512277",
              "p": "892646047623544832",
              "q": "895070743237386252",
              "r": "895073271622537287",
              "s": "892646047099265025",
              "t": "892646046684033055",
              "u": "892646047468355604",
              "v": "892646047363526686",
              "w": "892646047082512395",
              "x": "892646047434801182",
              "y": "892646047732629554",
              "z": "892646092288708628",
              "2": "895070743493218314",
              "3": "893415443451244565",
              " ": "815691302225313812"
            }
        }
        self.config.register_guild(**default_guild)

    # This cog does not store any End User Data
    async def red_get_data_for_user(self, *, user_id: int):
        return {}
    async def red_delete_data_for_user(self, *, requester, user_id: int) -> None:
        pass

    @commands.command()
    async def kyarutail(self, ctx, *, msgBody):
        """Prepare a Kyarutail message to send

        Prerequisites: NQN bot + joined Kyarutail server ([Why?](https://thymedev.github.io/coffee/kyarutail))

        It may be troublesome to type or access Kyarutail emotes. This cog will translate text (abc) into emotes (:kyaruA::kyaruB::kyaruC:) for [NQN bot](https://nqn.blue).
        """
        guildData = await self.config.guild(ctx.guild).all()
        ktData = guildData.get("kyaruEmotes", None)
        
        # catch
        if ktData == None:
          return await ctx.send("Error: No saved Kyarutail emotes.")

        # split into array and replace
        msgArray = list(msgBody.lower())
        sendMsg = ""
        for i in msgArray:
          ktLetter = ktData.get(str(i), None)
          if ktLetter:
            sendMsg += ":kyaru"+str(i).upper()+":"
          else:
            sendMsg += str(i)

        # Extra spacing
        sendMsg = sendMsg.replace(":kyaru :", "      ")

        await ctx.send("Copy-paste and send the following:", delete_after=12)
        e = discord.Embed(description=sendMsg, color=(await ctx.embed_colour()))
        sendMsgResult = await ctx.send(embed=e, delete_after=12)
        await sendMsgResult.add_reaction("🗑️")
        await sendMsgResult.add_reaction("3️⃣")
        await asyncio.sleep(4)
        await sendMsgResult.add_reaction("2️⃣")
        await asyncio.sleep(4)
        await sendMsgResult.add_reaction("1️⃣")
        return

    @commands.command()
    async def kyaruself(self, ctx, *, msgBody):
        """Send a Kyarutail message as yourself

        Due to Discord limitations, this may no longer work.
        
        Uses webhook when available. Falls back to bot message when not."""
        guildData = await self.config.guild(ctx.guild).all()
        ktData = guildData.get("kyaruEmotes", None)
        
        # catch
        if ktData == None:
          return await ctx.send("Error: No saved Kyarutail emotes.")

        # split into array and replace
        msgArray = list(msgBody.lower())
        sendMsg = ""
        for i in msgArray:
          ktLetter = ktData.get(str(i), None)
          if ktLetter:
            if ktLetter.isalpha() == True:
              sendMsg += "<:kyaru"+str(i)+":"+str(ktLetter)+">"
            else:
              sendMsg += "<:emote"+":"+str(ktLetter)+">"
          else:
            sendMsg += str(i)

        # Extra spacing
        sendMsg = sendMsg.replace(" ", "  ")

        # Send as webhook
        try:
            # Find a webhook that the bot made
            whooklist = await ctx.channel.webhooks()
            whurl = ""
            # Return if match
            for wh in whooklist:
                if self.bot.user == wh.user:
                    whurl = wh.url
            # Make new webhook if one didn't exist
            if whurl == "":
                newHook = await ctx.channel.create_webhook(name="Webhook")
                whurl = newHook.url

            webhook = SyncWebhook.from_url(whurl)
            webhook.send(
                sendMsg,
                username=ctx.author.display_name,
                avatar_url=ctx.author.display_avatar.url,
            )
        except discord.errors.Forbidden:
            return await ctx.send(sendMsg)
