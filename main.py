# https://www.notion.so/Big-Fred-56e28b634ebe40bebf062ea3cba837b6
# https://discordpy.readthedocs.io/en/latest/api.html#
# https://discordpy.readthedocs.io/en/latest/ext/commands

# We only have to be lucky once.
# You will have to be lucky always.

import discord
from discord.ext import commands

import os

import secrets

if __name__ == "__main__":
    bot: commands.Bot = commands.Bot(command_prefix="!", intents=discord.Intents.all(), case_insensitive=True)

    token = secrets.DISCORD_TOKEN

    print("Discord API Version {x.major}.{x.minor}".format(x=discord.version_info))

    print("\nLoading Cogs...")

    preload = ["fred_functions"]
    for cog in preload:
        bot.load_extension(f"cogs.{cog}")
        print(f"> Loaded {cog}.py")

    for cog in os.listdir("cogs"):
        if cog.split(".", 2)[-1] == "py" and cog[0] != "_":
            try:
                bot.load_extension("cogs." + cog[:-3])
                print(f"> Loaded {cog}")
            except discord.ext.commands.ExtensionAlreadyLoaded:
                pass

    print("Cogs Loaded\n")

    @bot.event
    async def on_ready():
        print(f"{bot.user.display_name} is online with a {round(bot.latency * 100, 2)}ms ping\n")

        print("Guilds:")
        for guild in bot.guilds:
            print(f"> {guild.name} ({len(guild.members)})")

    bot.run(token)
