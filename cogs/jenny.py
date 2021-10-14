# Fred's mum
import asyncio
import importlib
from discord.ext import commands
import os
import secrets


class Jenny(commands.Cog):

    @commands.command()
    async def update(self, ctx: commands.context):
        if ctx.guild.id == 891429195811545158 and secrets.HOSTER_ID == ctx.bot.user.id:
          
            for cog in os.listdir("cogs"):
                if self.can_edit(cog):
                    ctx.bot.unload_extension("cogs." + cog[:-3])
                    print(f"> Unloaded {cog}")
                    
            shell = await asyncio.create_subprocess_shell("git fetch --all && git reset --hard")
            await shell.wait()
            
            for cog in os.listdir("cogs"):
                if self.can_edit(cog):
                    ctx.bot.load_extension("cogs." + cog[:-3])
                    print(f"> Reloaded {cog}")
                    
            for file in os.listdir("."):
                if self.can_edit(file):
                    importlib.reload(importlib.import_module(file[:-3]))
                    print(f"> Reloaded {file}")

    @staticmethod
    def can_edit(name: str):
        return name.split(".", 2)[-1] == "py" and name[0] != "_" and name not in ["main.py", "jenny.py"]


def setup(bot: commands.Bot):
    bot.add_cog(Jenny(bot))
