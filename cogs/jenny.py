from discord.ext import commands
import os
import secrets


class Jenny (commands.Cog):

    @commands.command()
    async def update(self, ctx: commands.context):
        if ctx.guild.id == 891429195811545158 and secrets.HOSTER_ID[:-4] == "chen":
            os.system("git fetch --all")
            os.system("git reset --hard")


def setup(bot: commands.Bot):
    bot.add_cog(Jenny(bot))
