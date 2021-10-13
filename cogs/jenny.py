from discord.ext import commands
import os


class Jenny (commands.Cog):

    @commands.command()
    async def update(self, ctx: commands.context):
        if ctx.guild.id == 891429195811545158:
            os.system("git fetch --all")
            os.system("git reset --hard")


def setup(bot: commands.Bot):
    bot.add_cog(Jenny(bot))
