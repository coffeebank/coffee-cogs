import aiohttp
import asyncio
from collections import OrderedDict
import discord
from discord import Webhook, AsyncWebhookAdapter
import re

class Cherry():
  """Cherry Emotes is the engine behind interacting with emotes in chat for non-nitro users using webhooks."""

  def __init__(self, **kwargs):
      super().__init__()
      self.cherryChatEmoteBank = []


  # General Utility Commands

  def emoteAnimated(self, text):
    if re.search(r"(gif)", text):
      return True
    else:
      return False

  def emoteBuilder(self, emote=None, emoteName=None, emoteId=None, emoteAnimated=None, buildAnimated=True, buildNormal=True):
    if emote is not None:
      emoteName = emote.name
      emoteId = emote.id
      emoteAnimated = emote.animated
    if buildAnimated == True and emoteAnimated == True:
      return "<a:"+str(emoteName)+":"+str(emoteId)+">"
    elif buildNormal == True and emoteAnimated == False:
      return "<:"+str(emoteName)+":"+str(emoteId)+">"
    else:
      return False

  async def emoteParser(self, RegexEmoteText, sendMsg):
    matchEmotes = re.findall(RegexEmoteText, sendMsg)
    if len(matchEmotes) > 0:
      # Remove duplicates
      return list(OrderedDict.fromkeys(matchEmotes))
    else:
      return False

  async def webhookFinder(self, ctx, bot):
    # Find a webhook that the bot made
    try:
      whooklist = await ctx.channel.webhooks()
    except:
      return False
    # Return if match
    for wh in whooklist:
      if bot.user == wh.user:
        return wh.url
    # If the function got here, it means there isn't one that the bot made
    try:
      newHook = await ctx.channel.create_webhook(name="Emotes")
      return newHook.url
    # Could not create webhook, return False
    except:
      return False

  async def webhookSender(self, message, webhookUrl, sendMsg):
    async with aiohttp.ClientSession() as session:
      webhook = Webhook.from_url(webhookUrl, adapter=AsyncWebhookAdapter(session))
      try:
        await webhook.send(
            sendMsg,
            username=message.author.display_name,
            avatar_url=message.author.avatar_url,
        )
      except:
        return False
      else:
        return True


  # Utilities for 'emotesheet'
  # Enable pulling emotes from Emote Sheet
          
  def esheetFinder(self, emoteName, emoteStore):
    # Convert :emotename: to emotename
    emoteName = emoteName[1:-1]
    for es in emoteStore:
      # [1] is emote name
      if emoteName == es[1]:
        return es
    return False

  def esheetProcessor(self, sendMsg, emoteNames, emoteStore):
    for en in emoteNames:
      es = Cherry.esheetFinder(self, en, emoteStore)
      if es is not False:
        # [2] is emote url
        emoteId = re.findall(r"(?<=emojis/)(\d{16,20})(?=\.)", es[2])[0]
        # Build emote object
        emoteStr = Cherry.emoteBuilder(self,
          emoteName=es[1],
          emoteId=emoteId,
          emoteAnimated=Cherry.emoteAnimated(self, es[2])
        )
        sendMsg = re.sub(fr"({en})", emoteStr, sendMsg)
    return sendMsg


  # Utilities for 'recents'
  # Searches through channel's recent messages to find a match

  def recentsBankBuilder(self, cherryChatHistory, RegexFullEmoteSearch):
    recentsBankBuilder = []
    for msg in cherryChatHistory:
      recentsBankBuilder += re.findall(RegexFullEmoteSearch, msg.clean_content)
    if len(recentsBankBuilder) > 0:
      return list(OrderedDict.fromkeys(recentsBankBuilder))
    else:
      return False

  async def recentsHistRetriever(self, message, cherryRecentsCount):
    try:
      return await message.channel.history(limit=cherryRecentsCount).flatten()
    except:
      return False

  def recentsProcessor(self, sendMsg, recentsBankBuilder, emoteNames):
    for ee in recentsBankBuilder:
      for emoteInput in emoteNames:
        if emoteInput in ee:
          sendMsg = re.sub(fr"({emoteInput})", ee, sendMsg)
    return sendMsg


  # Utilities for 'server'
  # Searches through local server emotes to find a match

  async def serverBankBuilder(self, message, emoteNames):
    # Retrieve guildEmotes and build emoteBank
    guildEmotes = await message.guild.fetch_emojis()
    emoteBank = []
    for ee in emoteNames:
      # Catch non-emote :text:
      eeitem = await Cherry.serverEmoteRetriever(self, message, guildEmotes, ee)
      if eeitem is not False:
        emoteBank.append(eeitem)
    if len(emoteBank) > 0:
      return emoteBank
    else:
      return False

  async def serverEmoteRetriever(self, ctx, guildEmotes, emoteInput):
    # Remove the : from :emoteInput:
    emoteName = emoteInput[1:-1]
    for ee in guildEmotes:
      if emoteName == ee.name and ee.animated == True:
        return ee
    # If the function got here, it means emote didn't exist
    return False
