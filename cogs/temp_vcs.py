import discord
from discord.ext import commands
from cogs.fred_functions import FredFunctions
import time
import asyncio

class TempVCs(commands.Cog):

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.fred_functions: FredFunctions = bot.get_cog("FredFunctions")

    @commands.command(aliases=["vc"])
    async def create_vc(self, ctx: commands.Context, *args):


        if len(args) > 0:
            name = args[0]
        else:
            name = ctx.message.author.display_name + "'s VC"


        if len(args) > 1:
            if not args[1].isdigit():
                await FredFunctions.command_error(
                return

            else:
                size = int(args[1])
        else:
            size = 99

        if size > 0 or size < 2:
            await FredFunctions.command_error(ctx, ["name?", "size?"])
            return
        
        category = None
        for c in guild.categories:
            if c.name == "Custom VCs":
                category = c
                break

        if not category:
            category = await ctx.guild.create_category(name="Custom VCs", position=2)

        i = 0
        while (name + " " + str(i) if i > 0 else name) in [c.name for c in guild.voice_channels]:
            i += 1
        name = name + " " + str(i) if i > 0 else name

        channel = await guild.create_voice_channel(name=name, category=category, user_limit=size)
        await ctx.message.reply(f"`{name}` with size `{size}`.")

        channel_created = time.time()
        while time.time() - channel_created < 360 and not len(channel.members):
            await asyncio.sleep(1)

        while len(channel.members) != 0:
            await asyncio.sleep(1)

        await channel.delete()

        if len(category.channels) == 0:
            await category.delete()
            await ctx.message.reply(f"VC `{name}` was deleted.")


def setup(bot: commands.Bot):
    bot.add_cog(TempVCs(bot))
