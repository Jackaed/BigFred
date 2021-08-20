import discord
from discord.ext import commands


class FredFunctions(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    async def command_error(self, ctx: commands.Context, args=None):
        args = args if args else []

        command_title = f"{self.bot.command_prefix}[{ctx.command.name}|{'.'.join(ctx.command.aliases)}]"
        f_args = f"{' [' if len(args) > 0 else ''}{'] ['.join(args)}{']' if len(args) > 0 else ''}"

        embed = discord.Embed(title="Error", colour=discord.Colour.red())
        embed.description = f"Correct Usage: `{command_title}{f_args}`"

        await ctx.message.reply(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(FredFunctions(bot))
