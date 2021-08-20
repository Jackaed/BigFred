# https://www.notion.so/Big-Fred-56e28b634ebe40bebf062ea3cba837b6
# https://discordpy.readthedocs.io/en/latest/api.html#

# We only need to be lucky once.
# You need to be lucky every time.

import discord
from discord.ext import commands

import os

if __name__ == "__main__":
    bot: commands.Bot = commands.Bot(command_prefix=".", intents=discord.Intents.all(), case_insensitive=True)

    try:
        with open(".token") as f:
            token = f.read()
    except FileNotFoundError:
        raise FileNotFoundError("Could not find .token file")

    print("Discord API Version {x.major}.{x.minor}".format(x=discord.version_info))

    print("\nLoading Cogs...")

    for cog in os.listdir("cogs"):
        if cog.split(".", 2)[-1] == "py" and cog[0] != "_":
            bot.load_extension("cogs." + cog.strip(".py"))
            print(f"> Loaded {cog}")

    print("Cogs Loaded\n")

    @bot.event
    async def on_ready():
        print(f"{bot.user.display_name} is online with ({round(bot.latency * 100, 2)}ms latency)")

    bot.run(token)
