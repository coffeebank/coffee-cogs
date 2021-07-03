<p align="center">
  <img src="https://raw.githubusercontent.com/coffeebank/coffee-cogs/master/msgmover/preview.jpg" />
</p>

<h1 align="center">
  msgmover
</h1>

<h3 align="center">
  The Discord Bot for Moving Messages Between Channels and Servers
</h3>

<p align="center">
  <a href="https://github.com/coffeebank/coffee-cogs/wiki/Add-to-Discord">Add to your Discord ></a>
</p>

<p align="center">
  <a href="https://coffeebank.github.io/discord">Join the Support Discord ></a>
</p>

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

The code was designed to be privacy-respecting from the ground up:
- Only webhook links and their configs, as set by server owners, are stored per guild/server
- All messages are replicated with user profiles on for content credits, but can be masked under the webhook name for anonymity
- Edited/deleted message support was built such that the bot does not need to log message/webhook IDs after a message is "done"

This bot was partly inspired by an old 'Relays' cog. For some reason, despite Discord Webhooks growing in features, all relay-like bots seem to have disappeared into the void:
- None seemed to attempt to replicate original messages as sent in chats
- None were useful in migrating messages for merging dead channels
- None allowed me to forward bot output messages to multiple channels, especially bot command embeds

I am not aware of a bot that can be configurable to this extent. I am certainly not aware of one that is open-source, simply because we are talking about private message data. So I decided to make one.

This code has no affiliation with, no codebase relations to, and integrates in a completely different way from, any previous relay code I know of.


## Bot Commands

Type `[p]msgmover` to see everything **msgmover** can do.

- `[p]msgcopy`  
Copy existing messages to a new server  

- `[p]msgrelay`  
Forward new messages to a new channel/server
