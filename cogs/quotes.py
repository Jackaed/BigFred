import discord
from discord.ext import commands
from cogs.fred_functions import FredFunctions
from cogs.settings_manager import SettingsManager


class Quotes(commands.Cog):

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.fred_functions: FredFunctions = bot.get_cog("FredFunctions")

    @commands.command(aliases=["q"])
    async def quote(self, ctx: commands.Context, *args):
        if len(args) >= 2:
            if len(ctx.message.mentions) > 0:
                user: discord.User = ctx.message.mentions[0]
                name = user.display_name
                icon = user.avatar_url
            else:
                name = args[0]
                icon = None

            text = " ".join(args[1:])
            date = self.fred_functions.date()

        elif len(args) == 0 and ctx.message.reference:
            message: discord.Message = await ctx.fetch_message(ctx.message.reference.message_id)
            name = message.author.display_name
            icon = message.author.avatar_url
            text = message.content
            date = self.fred_functions.date(message.created_at)
        else:
            await self.fred_functions.command_error(ctx, ["@user|name", "message"], f"You can also reply to a message with `{self.bot.command_prefix}q` to quote it.")
            return

        embed = discord.Embed(colour=discord.Colour.blue())
        if icon:
            embed.set_author(name=name, icon_url=icon)
        else:
            embed.set_author(name=name)
        embed.description = f"**`{text}'**"
        embed.set_footer(text=date)

        settings: SettingsManager.settings = self.bot.get_cog("SettingsManager").get(ctx.guild.id)
        channel: discord.TextChannel = ctx.guild.get_channel(int(settings.channel_quotes.value[2:-1]))

        await channel.send(embed=embed)
        await ctx.message.reply(f"Quote sent to {channel.mention}")


def setup(bot: commands.Bot):
    bot.add_cog(Quotes(bot))
