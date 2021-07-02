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

**msgmover** is a Discord bot made for redirecting chats, merging Discord channels, and linking up two Discord servers. The two main features rely on the same technology:

- **msgcopy**: Copy existing messages from one Discord channel into another Discord channel  

- **msgrelay**: Forward all new messages from one Discord channel into another Discord channel


## How does it work?

Each user's profile picture, nickname/username, and message is copied and pasted into the new channel/server.

**Currently supported:**
- Embeds
- Attachments (Images, videos, text, etc.)
- Replies

**Not supported yet:**
- Syncing message edits
- Syncing message deletes


## Why?

This bot was partly inspired by an old 'Relays' cog, before all the "relay"-type cogs/bots and their derivatives seem to have disappeared into the void. This code has no affiliation with, no codebase relations to, and integrates in a completely different way from, any previous relay code I know of.

The code was designed to be privacy-respecting from the ground up. Only webhook links and configs are stored per-guild, and the messages are pushed to any provided webhooks, whether they point to another Discord channel, server, or something else altogether. Server admins can choose to mask messages from a variety of sources and redirect them to a customized webhook if they wish.

I am not aware of a bot that can redirect messages and is configurable to this extent, that is also free and open source, so I have created one.



## Bot Commands

Type `[p]help Msgmover` to see everything **msgmover** can do.

- `[p]msgcopy`  
Copy existing messages to a new server  

- `[p]msgrelay`  
Forward new messages to a new channel/server
