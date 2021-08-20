import discord
from discord.ext import commands


class Setting:
    def __init__(self, name: str, description: str, value = None):
        self.name = name
        self.value = value
        self.description = description

    @property
    def embed(self) -> discord.Embed:
        embed = discord.Embed(title=self.name, colour=discord.Colour.purple())
        embed.description = self.description
        embed.add_field(name="Current Value", value=self.value)
        embed.set_footer(text="Reply to this message to set a new value")
        return embed


class RoleSetting(Setting):
    def __init__(self, name: str, description: str, value: discord.Role = None):
        super().__init__(name, description, value)

    @property
    def embed(self) -> discord.Embed:
        return super().embed.set_footer(text="Reply to this message to set a new value (must be @role)")


class ChannelSetting(Setting):
    def __init__(self, name: str, description: str, value: discord.TextChannel = None):
        super().__init__(name, description, value)

    @property
    def embed(self) -> discord.Embed:
        return super().embed.set_footer(text="Reply to this message to set a new value (must be #channel)")


class SettingsChannels(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.settings: {str: [Setting]} = {
            "roles": [
                RoleSetting("Muted", "Role given to muted members"),
            ],

            "channels": [
                ChannelSetting("Quotes", "Channel Quotes are sent to"),
                ChannelSetting("Audit Log", "Channel that will contain the Audit Log"),
            ]
        }

    async def initialise(self):
        for guild in self.bot.guilds:
            guild: discord.Guild

            if "Big Fred" not in [cat.name for cat in guild.categories]:

                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(view_channel=False),
                    guild.me: discord.PermissionOverwrite(view_channel=True)
                }

                await guild.create_category("Big Fred", overwrites=overwrites)

            for category in guild.categories:
                category: discord.CategoryChannel

                if category.name == "Big Fred":
                    not_done_channels = list(self.settings.keys())

                    for channel in category.text_channels:
                        channel: discord.TextChannel

                        if channel.name in not_done_channels:
                            not_done_channels.remove(channel.name)

                            not_done_settings = [setting.name for setting in self.settings[channel.name]]

                            async for message in channel.history():
                                if len(message.embeds) == 1 and message.author == self.bot.user:
                                    if message.embeds[0].title in not_done_settings:
                                        not_done_settings.remove(message.embeds[0].title)

                            for setting in self.settings[channel.name]:
                                if setting.name in not_done_settings:
                                    await channel.send(embed=setting.embed)

                    for channel_name in not_done_channels:
                        new_channel = await guild.create_text_channel(channel_name, category=category)
                        await self._init_channel(new_channel)

    async def _init_channel(self, channel: discord.TextChannel):
        settings = self.settings[channel.name]
        for setting in settings:
            await channel.send(embed=setting.embed)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.reference:
            channel: discord.TextChannel = self.bot.get_channel(message.reference.channel_id)
            replying_to: discord.Message = await channel.get_partial_message(message.reference.message_id).fetch()

            if len(replying_to.embeds) == 1 and replying_to.author == self.bot.user:
                if replying_to.embeds[0].colour != discord.Colour.purple():
                    return
            else:
                return

            for setting in self.settings[channel.name]:
                if setting.name == replying_to.embeds[0].title:
                    value = message.content
                    response = "Updated"

                    if isinstance(setting, RoleSetting):
                        if len(message.role_mentions) == 0:
                            value = None
                            response = "Must be @role"
                        else:
                            value = message.content

                    elif isinstance(setting, ChannelSetting):
                        if len(message.channel_mentions) == 0:
                            value = None
                            response = "Must be #channel"
                        else:
                            value = message.content

                    if value:
                        setting.value = value
                        await replying_to.edit(embed=setting.embed)

                    await message.delete(delay=1)
                    confirmation = await message.reply(response)
                    await confirmation.delete(delay=1)


def setup(bot: commands.Bot):
    bot.add_cog(SettingsChannels(bot))
