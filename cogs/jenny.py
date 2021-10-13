import asyncio
import importlib
from discord.ext import commands
import os
import secrets


class Jenny (commands.Cog):

    @commands.command()
    async def update(self, ctx: commands.context):
        if ctx.guild.id == 891429195811545158 and secrets.HOSTER_ID[-4:] == "chen":
            for cog in os.listdir("cogs"):
                if cog.split(".", 2)[-1] == "py" and cog[0] != "_" and cog != "jenny.py":
                    ctx.bot.unload_extension("cogs." + cog[:-3])
                    print(f"> Unloaded {cog}")
            wait = await asyncio.create_subprocess_shell("git fetch --all && git reset --hard")
            await wait.wait()
            for cog in os.listdir("cogs"):
                if cog.split(".", 2)[-1] == "py" and cog[0] != "_" and cog != "jenny.py":
                    ctx.bot.load_extension("cogs." + cog[:-3])
                    print(f"> Reloaded {cog}")
            for imp in os.listdir("."):
                if imp.split(".", 2)[-1] == "py" and imp[0] != "_" and imp != "main.py":
                    importlib.reload(importlib.import_module(imp[:-2]))
                    print(f"> Reloaded {imp}")


def setup(bot: commands.Bot):
    bot.add_cog(Jenny(bot))
