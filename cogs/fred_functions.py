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

    @staticmethod
    def contains_image(message: discord.Message):

        image_file_formats = ["png", "jpeg", "jpg"]

        if not message.attachments:
            return False

        file = message.attachments[0].url

        for file_format in image_file_formats:
            if file[-len(file_format):].lower() == file_format:
                return True

        return False

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        logs: discord.TextChannel = self.bot.get_channel(901921091705004134)
        if message.author == self.bot.user:
            return

        if message.channel != logs and message.guild:
            embed = discord.Embed(colour=discord.Colour.random(seed=message.guild.id), description=message.content)
            embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
            embed.set_footer(text=message.guild.name, icon_url=message.guild.icon_url)
            await logs.send(embed=embed)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        errors: discord.TextChannel = self.bot.get_channel(901921500226011146)
        error = getattr(error, 'original', error)
        embed = discord.Embed(title="Error", colour=discord.Colour.red(), description=error)
        await errors.send(embed=embed)
        await ctx.reply(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(FredFunctions(bot))
