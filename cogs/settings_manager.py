import discord
from discord.ext import commands
from cogs.fred_functions import FredFunctions

import pickle
import os
from collections import namedtuple

Setting = namedtuple("Setting", ["value", "name", "type", "list", "description"])


class Settings:

    def __init__(self):
        self.role_muted: Setting = Setting(None, "Muted Role", "role", False, "Role given to mute members")
        self.roles_join: Setting = Setting(None, "Join Role", "role", True, "Roles given to members when they join")

        self.channel_quotes: Setting = Setting(None, "Quotes Channel", "channel", False, "Channel Quotes are sent to")
        self.channel_greeting: Setting = Setting(None, "Greetings Channel", "channel", False, "Channel Greeting messages are sent to")

        self.message_join: Setting = Setting(None, "Join Message", "str", False, "Message sent to when a member joins")
        self.dm_join: Setting = Setting(None, "Join DM", "str", False, "DM sent to member when they join")


class SettingsManager(commands.Cog):

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.fred_functions: FredFunctions = bot.get_cog("FredFunctions")

        os.makedirs("settings", exist_ok=True)

    @staticmethod
    def get(guild_id: int) -> Settings:
        try:
            with open(f"settings/{guild_id}.fred", "rb") as f:
                file = pickle.load(f)
            return file
        except FileNotFoundError:
            return Settings()

    @staticmethod
    def set(guild_id: int, settings: Settings):
        with open(f"settings/{guild_id}.fred", "wb") as f:
            pickle.dump(settings, f)

    @commands.command()
    async def reset_settings(self, ctx: commands.Context):
        self.set(ctx.guild.id, Settings())

    @commands.command(aliases=["setting"])
    async def settings(self, ctx: commands.Context, setting_name: str = None, value_str: str = None):
        guild_id: int = ctx.guild.id
        settings = self.get(guild_id)

        if not setting_name:
            embed = discord.Embed(title="Settings", colour=discord.Colour.orange(),
                                  description=f"Use `{self.bot.command_prefix}settings [setting] [value?]` to manage a setting")

            for attribute in vars(settings):
                setting: Setting = getattr(settings, attribute)

                value = setting.value if setting.value else '`Not Set`'
                if setting.list and setting.value:
                    value = " ".join(setting.value)

                if setting.type == "str" and setting.value:
                    value = f"\"{value}\""

                embed.add_field(name=setting.name, value=f"{value}\n`{self.bot.command_prefix}settings {attribute}`", inline=True)

            embed.description += f"\nUse `{self.bot.command_prefix}reset_settings` to reset all settings"

            await ctx.reply(embed=embed)

            return

        if setting_name not in vars(settings):
            await self.fred_functions.command_error(ctx, ["setting?", "value?"], f"`{setting_name}` is not a setting. " 
                                                                                 f"Run `{self.bot.command_prefix}settings` to see all settings.")
            return

        setting = getattr(settings, setting_name)

        if not value_str:
            embed = await self._setting_embed(setting_name, guild_id)
            await ctx.reply(embed=embed)

            return

        new_value = None
        if setting.type == "str":
            new_value = value_str
        else:
            if setting.type == "role":
                looking_for = ctx.message.role_mentions
            else:
                looking_for = ctx.message.channel_mentions

            looking_for = [v.mention for v in looking_for]

            if setting.list:
                if len(looking_for) > 0:
                    new_value = looking_for
            else:
                if len(looking_for) == 1:
                    new_value = looking_for[0]

        if setting:
            # noinspection PyProtectedMember
            setattr(settings, setting_name, getattr(settings, setting_name)._replace(value=new_value))
            self.set(guild_id, settings)

            embed = await self._setting_embed(setting_name, guild_id)
            await ctx.reply(embed=embed)
        else:
            await self.fred_functions.custom_error(ctx, f"Couldn't Change {setting.name}", f"Invalid type supplied, must be `{setting.type}`")

    async def _setting_embed(self, setting_name: str, guild_id: int) -> discord.Embed:
        setting: Setting = getattr(self.get(guild_id), setting_name)

        embed = discord.Embed(title=f"{setting.name}", colour=discord.Colour.orange())
        embed.description = f"{setting.description}"

        value = setting.value if setting.value else '`Not Set`'
        if setting.list and setting.value:
            value = " ".join(setting.value)

        embed.add_field(name="Current Value", value=f"{value}", inline=True)
        embed.add_field(name="List", value=f"`{setting.list}`", inline=True)
        embed.add_field(name="Change Command", value=f"`{self.bot.command_prefix}settings {setting_name} [value]`", inline=False)

        return embed


def setup(bot: commands.Bot):
    bot.add_cog(SettingsManager(bot))
