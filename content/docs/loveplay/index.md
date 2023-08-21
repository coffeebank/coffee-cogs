---
title: "loveplay"
description: "Send love to other members of the server with reaction gifs from Purrbot API. Does not require a user @mention (say '=hug server' all you like!). Includes: blush, cuddle, dance, hug, kiss, lick, neko, nom, pat, poke, slap. Also includes a custom reaction gif builder that works for any gif type from the Purrbot API."
---

# loveplay

<component-coghero cog="loveplay" desc="Send love to other members of the server with reaction gifs from Purrbot API. Does not require a user @mention (say '=hug server' all you like!). Includes: blush, cuddle, dance, hug, kiss, lick, neko, nom, pat, poke, slap. Also includes a custom reaction gif builder that works for any gif type from the Purrbot API."></component-coghero>


## Getting Started

Because this cog replaces the  `hug`  command, you will need to unload the  `General`  cog from your Red bot. There is a custom replacement in  `coffeetools`  cog but it is currently incomplete.


## Custom Commands

Loveplay is flexible. You can create a custom command at any time.

The Purrbot Image API lists all image types at https://docs.purrbot.site/api/.

In the  `[p]loveplay`  command, you can use any image type as your "action" and insert a description (in quotes if there are multiple words).

When you are done, you can use  `[p]alias`  command to create any custom Loveplay command you'd like.


### Example

`[p]loveplay bite "nom 🤤" @PuddingUser`
- action: bite, description: "nom 🤤"
- ![Running the command `[p]loveplay bite "nom 🤤" @PuddingUser`](./loveplay-example-01.jpg)
- alias command: [p]bite
- ![Running the command `[p]alias add bite loveplay bite "nom 🤤"`, which adds a new command `[p]bite`](./loveplay-example-02.jpg)



## FAQ

### My aliases are returning something weird!

On 18 June 2023, a breaking change to the main Loveplay command switched the user input to the end of the command. Loveplay has decided to enable this change to make custom aliases easier and allow for smoother multi-word use of the Loveplay command.

This may have affected certain aliases that have been already set up. Please update/edit your aliases and remove the `{0}`. With this change, the `user` parameter is automatic, and supports multi-word entries without needing `""` double-quotes.

Please note the `description` still needs to be in `""` double-quotes if it is multi-word, when setting up the alias.
