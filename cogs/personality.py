import discord
from discord.ext import commands
from cogs.fred_functions import FredFunctions
import messages

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
            await message.channel.send(random.choice(messages.PING))

        if random.random() * 100 < messages.CHANCE_EMOJI:
            await message.add_reaction(random.choice(messages.EMOJI))

        if random.random() * 100 < messages.CHANCE_GUILD_EMOJI:
            await message.add_reaction(random.choice(message.guild.emojis))

        if random.random() * 100 < messages.CHANCE_MESSAGE:
            await message.channel.send(random.choice(messages.RANDOM))

        if random.random() * 100 < messages.CHANCE_DM:
            member: discord.Member = message.author

            await member.send(random.choice(messages.DM))

        if random.random() * 100 < messages.CHANCE_STATUS_CHANGE:
            await self.bot.change_presence(activity=random.choice(messages.STATUSES))


def setup(bot: commands.Bot):
    bot.add_cog(Personality(bot))
