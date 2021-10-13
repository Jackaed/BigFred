import discord
from discord.ext import commands
import os
import secrets


class Jenny(commands.Cog):

    @commands.command()
    async def update(self, ctx: commands.context):
        embed = discord.Embed(title="Jenny", colour=discord.Colour.orange())

        if ctx.guild.id == 891429195811545158 and secrets.HOSTER_ID == 840663909655379990:
            os.system("git fetch --all")
            os.system("git reset --hard")
            embed.description = "Updated"
        else:
            embed.description = "Command must be run from Fred's Palace and be hosted by Fred"

        await ctx.reply(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Jenny(bot))
