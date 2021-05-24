from collections import OrderedDict
import discord
import re

class Cherry():
  """Cherry Emotes is the engine behind interacting with emotes in chat for non-nitro users using webhooks."""

  # Scaffolding for splitting a single cog.py file into many smaller
  # files is inspired by https://github.com/aikaterna/aikaterna-cogs/
  # (MIT license, no affiliation)

  def __init__(self, **kwargs):
      super().__init__()
      self.cherryChatEmoteBank = []


  # General Utility Commands

  async def cherryEmoteParser(self, RegexEmoteText, sendMsg):
    matchEmotes = re.findall(RegexEmoteText, sendMsg)
    if len(matchEmotes) > 0:
      # Remove duplicates
      return list(OrderedDict.fromkeys(matchEmotes))
    else:
      return False

  async def cherryWebhookFinder(self, ctx, bot):
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


  # Utilities for 'server'
  # Searches through local server emotes to find a match

  async def cherryEmoteBank(self, message, emoteNames):
    # Retrieve guildEmotes and build emoteBank
    guildEmotes = await message.guild.fetch_emojis()
    emoteBank = []
    for ee in emoteNames:
      # Catch non-emote :text:
      eeitem = await Cherry.cherryGetEmoteFromGuild(self, message, guildEmotes, ee)
      if eeitem is not False:
        emoteBank.append(eeitem)
    if len(emoteBank) > 0:
      return emoteBank
    else:
      return False

  def cherryEmoteBuilder(self, emote, buildAnimated=True, buildNormal=True):
    if buildAnimated == True and emote.animated == True:
      return "<a:"+str(emote.name)+":"+str(emote.id)+">"
    elif buildNormal == True and emote.animated == False:
      return "<:"+str(emote.name)+":"+str(emote.id)+">"
    else:
      return False

  async def cherryGetEmoteFromGuild(self, ctx, guildEmotes, emoteInput):
    # Remove the : from :emoteInput:
    emoteName = emoteInput[1:-1]
    for ee in guildEmotes:
      if emoteName == ee.name and ee.animated == True:
        return ee
    # If the function got here, it means emote didn't exist
    return False


  # Utilities for 'recents'
  # Searches through channel's recent messages to find a match

  async def cherryGetChatHistory(self, message, cherryRecentsCount):
    try:
      return await message.channel.history(limit=cherryRecentsCount).flatten()
    except:
      return False

  def cherryHistEmoteBank(self, cherryChatHistory, RegexFullEmoteSearch):
    cherryHistEmoteBank = []
    for msg in cherryChatHistory:
      cherryHistEmoteBank += re.findall(RegexFullEmoteSearch, msg.clean_content)
    if len(cherryHistEmoteBank) > 0:
      return list(OrderedDict.fromkeys(cherryHistEmoteBank))
    else:
      return False

  def cherryHistInsertEmotes(self, sendMsg, cherryHistEmoteBank, emoteNames):
    for ee in cherryHistEmoteBank:
      for emoteInput in emoteNames:
        if emoteInput in ee:
          sendMsg = re.sub(fr"({emoteInput})", ee, sendMsg)
    return sendMsg
