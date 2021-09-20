import discord
from discord.ext import commands
from cogs.fred_functions import FredFunctions
from constants import Messages

import random


class Personality(commands.Cog):

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.fred_functions: FredFunctions = bot.get_cog("FredFunctions")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return

        if "skrillex" in message.content.lower():
            response = await message.reply("Do not talk about that here.")
            await message.delete(delay=5)
            await response.delete(delay=5)

        if self.bot.user.mentioned_in(message):
            await message.channel.send(random.choice(Messages.PING))

        if random.random() * 100 < Messages.CHANCE_EMOJI:
            await message.add_reaction(random.choice(Messages.EMOJI))

        if random.random() * 100 < Messages.CHANCE_GUILD_EMOJI:
            await message.add_reaction(random.choice(message.guild.emojis))

        if random.random() * 100 < Messages.CHANCE_MESSAGE:
            await message.channel.send(random.choice(Messages.RANDOM))

        if random.random() * 100 < Messages.CHANCE_DM:
            member: discord.Member = message.author

            await member.send(random.choice(Messages.CHANCE_DM))

        if random.random() * 100 < Messages.CHANCE_STATUS_CHANGE:
            await self.bot.change_presence(activity=random.choice(Messages.STATUSES))


def setup(bot: commands.Bot):
    bot.add_cog(Personality(bot))
