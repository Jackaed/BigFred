import string

import discord
from discord.ext import commands
from cogs.fred_functions import FredFunctions


class Polls(commands.Cog):

    option_emojis = ['🇦', '🇧', '🇨', '🇩', '🇪']

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.fred_functions: FredFunctions = bot.get_cog("FredFunctions")

    @commands.command()
    async def poll(self, ctx: commands.Context, title=None, *options):
        if not title or len(options) > 5:
            await self.fred_functions.command_error(ctx, ["title", "option1? .. option5?"])
            return

        if len(options) == 0:
            options = ("Yes", "No")

        embed = self.generate_poll_embed(title, options, ctx.author)

        message: discord.Message = await ctx.reply(embed=embed)

        for i in range(len(options)):
            await message.add_reaction(Polls.option_emojis[i])

    @staticmethod
    def generate_poll_embed(title: str, options: [str], author: discord.User, votes: [int] = None) -> discord.Embed:
        embed = discord.Embed(title=title, colour=discord.Colour.blue())

        embed.description = "React to vote"

        text = ""

        for i in range(len(options)):
            text += f"{Polls.option_emojis[i]} {options[i]}"
            if i < len(options) - 1:
                text += "\n"

        if not votes:
            votes = [0] * 5

        total = sum(votes) + 0.000001

        embed.add_field(name="Reaction", value="\n".join([f"{Polls.option_emojis[i]}" for i in range(len(options))]), inline=True)
        embed.add_field(name="Option", value="\n".join([f"{option}" for option in options]), inline=True)
        embed.add_field(name="Votes", value="\n".join([f"{vote} ({round(vote / total * 100)}%)" for vote in votes[:len(options)]]), inline=True)

        embed.set_footer(text=author.display_name, icon_url=author.avatar_url)

        return embed

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        await self.reaction_updated(payload)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        await self.reaction_updated(payload)

    async def reaction_updated(self, payload: discord.RawReactionActionEvent):
        channel: discord.TextChannel = self.bot.get_channel(payload.channel_id)
        message: discord.Message = await channel.fetch_message(payload.message_id)
        user = await self.bot.fetch_user(payload.user_id)

        if user == self.bot.user or len(message.embeds) != 1:
            return

        embed: discord.Embed = message.embeds[0]
        if embed.description != "React to vote":
            return

        options = []
        votes = []

        for field in message.embeds[0].fields:
            if field.name == "Option":
                for option in field.value.split("\n"):
                    options.append(option)

        for reaction in message.reactions:
            reaction: discord.Reaction
            votes.append(reaction.count - 1)

        new_embed = self.generate_poll_embed(embed.title, options, user, votes)

        await message.edit(embed=new_embed)


def setup(bot: commands.Bot):
    bot.add_cog(Polls(bot))
