---
title: "msgmover"
description: "The Discord Bot for Moving Messages Between Channels and Servers. Copy messages from one channel to another, or continuously relay messages to other channels/servers. Make moving messages between channels/servers easy and integrated, using webhooks."
---

<img src="./msgmover.jpg" alt="Logo: a handful of letters, spread out on a table" class="h-24 aspect-square rounded mb-2" />

# Msgmover

<component-coghero cog="msgmover" desc="Make moving messages between channels/servers easy and integrated, using webhooks. &#13;&#13;msgcopy: Copy messages from one channel to another. Move whole conversations, or merge channels easily with re-uploaded attachments, bot messages, and usernames/profiles replicated in full. Includes timestamp spacers. &#13;&#13;msgrelay: Relay messages from one channel to another channel/server. Supports usernames/profile pics, replies, attachments (files/images/video), and embeds (bot command replies). Supports edited/deleted messages. Supports forwarding to multiple webhooks/channels. Forward messages between different servers to bridge communities and share content."></component-coghero>

<div class="text-center py-6">
  <h3>The Discord Bot for Moving Messages Between Channels and Servers</h3>
  <p>
    <a href="/coffee/start">Add to your Discord ></a>
  </p>
  <p>
    <a href="/discord">Join the Support Discord ></a>
  </p>
</div>


## What is msgmover?

Make moving messages between channels/servers easy and integrated, using webhooks.

- **msgcopy**: Copy messages from one channel to another. Move whole conversations, or merge channels easily with re-uploaded attachments, bot messages, and usernames/profiles replicated in full. Includes timestamp spacers.  

- **msgrelay**: Relay messages from one channel to another channel/server. Forward messages between different servers to bridge communities and share content. Supports:
  - Usernames/profile pics, replies, attachments (files/images/video), and embeds (bot command replies)
  - Edited/deleted messages
  - Forwarding to multiple webhooks/channels 


## How does it work?

Each user's profile picture, nickname/username, and message is copied and pasted into the new channel/server.

**Currently supported:**
- Embeds
- Attachments (Files/images/videos)
- Replies
- Message edits
- Message deletes

**Not supported yet:**
- Reactions


## Why?

Despite Discord Webhooks growing in features, all relay-like bots seem to have disappeared into the void.

My hope for Msgmover was to:
- Migrate messages, for merging dead channels and moving conversations to other channels
  - No more mods copy-pasting half the chat into another channel
- Replicate all messages (including bot replies/embeds) as sent in chats
  - Pretty-print all the messages, **including bot replies/embeds**, which may be taboo for some, but required as an essential part of this feature
- Forward all messages (including bot replies/embeds) to multiple channels
  - Discord has finally introduced announcement channels, but they still don't work for bot messages yet (ie. an RSS feed from a bot + a chat room shared between multiple servers)

This bot was partly inspired by an old 'Relays' cog from the Red DiscordBot community. However, this code has no affiliation with, no codebase relations to, and integrates in a completely different way from, any previous relay code I know of.


### Freedom of moved messages

Some may have concerns with losing the right to edit/delete your messages if your message has been moved using this bot.

What Msgmover **cannot** guarantee is that server owners/admins use this bot responsibly:
- If anyone wanted to move a conversation, the common solution is already to (a) copy-paste half the chat and paste it elsewhere, or (b) screenshot the chat -- Msgmover only makes the chat look nicer.
- The concept of asking for server owners/admins to optionally delete messages is also standard (ie. when there is a server raid), and can be extended by asking them to delete moved messages.
- Server owners/admins who do not respect user freedoms already use moderation bots that log edited/deleted messages, stored in Discord forever without your ability to know about it or delete it.

What Msgmover **can** guarantee is that when messages are moved:
- All messages are replicated with user profiles for content credits, using server nicknames by default (instead of leaking the username#1234), or optionally masked under the webhook name altogether in Msgrelays
- Edited/deleted message support was built such that the bot does not need to log message/webhook IDs after a message is "done"
- Only webhook links and their configs, as set by server owners, are stored per guild/server. Msgmover does not log anything else -- no message IDs, no user IDs, nothing.

Of course, the discussion on moved messages is irrelevant in the first place if you are using Msgmover in a small server where everyone has admin/message delete permissions (ie. with friends).

This was the initial motive for this bot: when everyone consents and you are cleaning up channels, but copy-pasting won't move bot messages or images, and screenshots would take too long.


## Bot Commands

Type `[p]msgmover` to see everything **msgmover** can do.

- `[p]msgcopy`  
Copy existing messages to a new server  

- `[p]msgrelay`  
Forward new messages to a new channel/server

<br />


## FAQ

### **The bot is returning an error in sending messages**

#### 2022-10-10

> Bad Request (error code: 50035): Invalid Form Body
> In username: Username cannot be "឵                     ឵"

- An error for an empty username for the timestamp has been fixed in two updates, released 10 October 2022. Please run `[p]cog update msgmover` to update.
