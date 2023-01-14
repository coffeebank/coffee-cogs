# Getting Started

**Coffee Cogs ☕** is a collection of Discord Bot extensions ("cogs") built for users with a self-hosted instance of [Red Discord Bot](https://github.com/Cog-Creators/Red-DiscordBot).

Setup is as easy as 1-2-3:

<div class="grid grid-cols-1 sm:grid-cols-3 text-lg font-bold text-center select-none">
  <div class="p-4 bg-black/5"><span class="text-sm">Step 1</span><br />Setup</div>
  <div class="p-4 bg-red-900/10"><span class="text-sm">Step 2</span><br />Download Red Bot</div>
  <div class="p-4 bg-indigo-900/10"><span class="text-sm">Step 3</span><br />Add to your Discord</div>
</div>

<br />

## What is Red Discord Bot?

![Explainer: Red Discord Bot is a platform. Coffee Cogs is a repository ("repo") of extensions ("cogs") that are built on top of Red Discord Bot.](/img/red-cogs-explainer.png)

To use any bot in **Coffee Cogs ☕**, you must first install Red Discord Bot.

Then, you can install the bots from **Coffee Cogs ☕** as extensions.

You can also [install many other cogs by the Red community](https://index.discord.red).

<br />

## Step 1: Setup

Click one below to begin:

### Windows

<details class="pt-3 pb-1 px-4 bg-black/5">
<summary class="cursor-pointer">
  <span class="font-bold px-4 pb-1">Start in Windows (Use your own PC)</span>
  <p>By using Windows, your bot will only run when your PC is on. If you turn your PC off, your bot will also be turned off.</p>
</summary>

To get started, set up WSL2 with the walkthrough below:

<ReactFrame to="https://www.youtube.com/embed/5EgV91-f1co?start=0&end=249&version=3&autoplay=0&modestBranding=1&rel=0&showinfo=0"></ReactFrame>

> 4:06  
> Stop here. Move to Step 2 below to continue.

</details>

### Cloud Server

<details class="pt-3 pb-1 px-4 bg-black/5">
<summary class="cursor-pointer">
  <span class="font-bold px-4 pb-1">Start in a Cloud Server (Amazon AWS, Google GCP, Linux, etc.)</span>
  <p>A "cloud server" is a fancy word for "a PC that's on 24/7, run by a company". These are usually paid (computers are expensive!), and run with Linux.</p>
</summary>

This guide will focus on a cloud server with a generous free plan: Google Cloud Platform (GCP).

Here is how to set up Google Cloud Platform:

<ReactFrame to="https://www.youtube.com/embed/-6u1NHKgqao?start=0&end=345&version=3&autoplay=0&modestBranding=1&rel=0&showinfo=0"></ReactFrame>

> 3:21  
> Use e2-micro instead. The f1-micro instance no longer exists.  
> https://cloud.google.com/free/docs/gcp-free-tier/#compute

> 4:09  
> Choose Ubuntu 2204  

> 4:21  
> Change the disk to "Standard persistent disk"  
> Change the storage to 20 GB  
> These will stay within the Free tier limits

<br />

</details>

<br />

## Step 2: Download Red DiscordBot

![gcp-ssh.png](/img/gcp-ssh.png)

After the setup above, you should see a console with a similar screen above.

Click this link to see setup instructions:

<ReactButton to="https://docs.discord.red/en/stable/install_guides/ubuntu-2204.html" body="Installing Red DiscordBot" newTab="true"></ReactButton>

For each line of code in the link above, copy-paste into your console and press enter.

Wait for each line to finish running before continuing.

<br />

## Step 3: Add your bot to your Discord server

<ReactButton to="https://docs.discord.red/en/stable/getting_started.html" body="Getting Started" newTab="true" className="mt-2"></ReactButton>

After adding to your Discord server and making sure the bot works, you're ready!

1. Browse the list of Coffee Cogs ☕ (see left sidebar) and find one you like!
2. You will see an **Install** box.
3. Copy-paste the commands there and enter them one-at-a-time into any Discord channel your bot can see.

> Replace [p] with your prefix  
> Replace %%%% with the name of the cog you want
```
[p]repo add coffee-cogs https://github.com/coffeebank/coffee-cogs
[p]cog install coffee-cogs %%%%%
```

<br />

## Enjoy :)

You're done! Join the Support Discord if you have any questions:

<ReactButton to="https://coffeebank.github.io/discord" body="Support Discord" newTab="true"></ReactButton>
