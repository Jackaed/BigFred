from discord.ext import commands

from cogs.fred_functions import FredFunctions


class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.fred_functions: FredFunctions = bot.get_cog("FredFunctions")

    @commands.command(aliases=["q"])
    async def quote(self, ctx: commands.Context, *args):
        if len(args) == 2:
            pass
        elif len(args) == 1:
            pass
        else:
            await self.fred_functions.command_error(ctx)
            return


def setup(bot: commands.Bot):
    bot.add_cog(Utilities(bot))
