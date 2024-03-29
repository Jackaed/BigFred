import discord
from discord.ext import commands
from cogs.fred_functions import FredFunctions
from cogs.settings_manager import SettingsManager


class Quotes(commands.Cog):

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.fred_functions: FredFunctions = bot.get_cog("FredFunctions")

    # noinspection PyUnboundLocalVariable
    @commands.command(aliases=["q"])
    async def quote(self, ctx: commands.Context, *args):

        image = None
        text = None
        icon = None

        valid = False

        # !q <member> <text>
        if len(args) >= 1:

            date = self.fred_functions.date()

            if FredFunctions.contains_image(ctx.message):
                image = ctx.message.attachments[0].url
                valid = True

            if len(args) >= 2:
                text = " ".join(args[1:])
                valid = True

            if len(ctx.message.mentions) > 0:
                user: discord.User = ctx.message.mentions[0]
                name = user.display_name
                icon = user.avatar_url
            else:
                name = args[0]

        # !q <@message>
        elif len(args) == 0 and ctx.message.reference:
            valid = True
            message: discord.Message = await ctx.fetch_message(ctx.message.reference.message_id)

            name = message.author.display_name
            icon = message.author.avatar_url
            text = message.content

            if message.attachments:
                image = message.attachments[0].url

            date = self.fred_functions.date(message.created_at)

        if not valid:
            await self.fred_functions.command_error(ctx, ["@user|name", "message"],
                                                    f"You can also reply to a message with `{self.bot.command_prefix}q` to quote it.")
            return

        embed = discord.Embed(colour=discord.Colour.blue())
        embed.set_author(name=name)
        if icon:
            embed.set_author(name=name, icon_url=icon)

        if text:
            embed.description = f"'{text}'"

        if image:
            embed.set_image(url=image)

        embed.set_footer(text=date)

        settings: SettingsManager.settings = self.bot.get_cog("SettingsManager").get(ctx.guild.id)
        channel: discord.TextChannel = ctx.guild.get_channel(int(settings.channel_quotes.value[2:-1]))

        await channel.send(embed=embed)
        await ctx.message.reply(f"{channel.mention}")


def setup(bot: commands.Bot):
    bot.add_cog(Quotes(bot))
