import discord
from discord.ext import commands
import datetime


class FredFunctions(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    async def command_error(self, ctx: commands.Context, args=None, description=None):
        args = args if args else []

        command_title = f"{self.bot.command_prefix}[{ctx.command.name}{'|' if len(ctx.command.aliases) > 0 else ''}{'|'.join(ctx.command.aliases)}]"
        f_args = f"{' [' if len(args) > 0 else ''}{'] ['.join(args)}{']' if len(args) > 0 else ''}"

        embed = discord.Embed(title="Error Running Command", colour=discord.Colour.red())
        embed.description = f"Correct Usage: `{command_title}{f_args}`"
        if description:
            embed.description += f"\n{description}"

        await ctx.message.reply(embed=embed)

    @staticmethod
    async def custom_error(ctx: commands.Context, title: str, description: str):
        await ctx.message.reply(embed=discord.Embed(title=title, description=description, colour=discord.Colour.red()))

    @staticmethod
    def date(time: datetime.datetime = None) -> str:
        if time is None:
            time = datetime.datetime.now()

        return time.strftime("%d %B %Y, %H:%M")


def setup(bot: commands.Bot):
    bot.add_cog(FredFunctions(bot))
