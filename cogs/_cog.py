import discord
from discord.ext import commands
from cogs.fred_functions import FredFunctions


class Cog(commands.Cog):

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.fred_functions: FredFunctions = bot.get_cog("FredFunctions")


def setup(bot: commands.Bot):
    bot.add_cog(Cog(bot))
