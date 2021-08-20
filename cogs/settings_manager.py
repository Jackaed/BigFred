from discord.ext import commands
from cogs.fred_functions import FredFunctions

import pickle
import os


class Settings:
    def __init__(self):

        self.role_muted: int = -1
        self.roles_join: [int] = []

        self.chan_quotes: int = -1
        self.chan_gretting: int = -1

        self.message_join: str = ""
        self.dm_join: str = ""


class SettingsManager(commands.Cog):

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.fred_functions: FredFunctions = bot.get_cog("FredFunctions")

        os.makedirs("settings", exist_ok=True)

    @staticmethod
    def get(guild_id: str) -> Settings:
        with open(f"settings/{guild_id}.fred", "rb") as f:
            file = pickle.load(f)

        return file

    @staticmethod
    def set(guild_id: int, settings: Settings):
        with open(f"settings/{guild_id}.fred", "wb") as f:
            pickle.dump(settings, f)


def setup(bot: commands.Bot):
    bot.add_cog(SettingsManager(bot))
