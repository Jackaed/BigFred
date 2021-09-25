import asyncio
import discord
import os
from discord.ext import commands
import youtube_dl
from cogs.fred_functions import FredFunctions


class MusicPlayer(commands.Cog):

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.fred_functions: FredFunctions = bot.get_cog("FredFunctions")

        self.clients: {int: discord.VoiceClient} = {}

    @commands.command(aliases=["p", "resume", "r"])
    async def play(self, ctx: commands.Context, *args):

        if ctx.message.author.voice is None:
            await self.fred_functions.custom_error(ctx, "User not in VC", "You need to be in a voice channel to use this command.")
            return

        if ctx.guild.id in self.clients and self.clients[ctx.guild.id].is_paused():
            self.clients[ctx.guild.id].resume()
            await ctx.reply("Resumed")
            return

        query = " ".join(args) if args else "James May says Cheese"

        user = ctx.message.author
        voice_channel = user.voice.channel

        try:
            voice_client = await voice_channel.connect()
        except discord.ClientException:
            # TODO: This will not work across guilds
            voice_client = self.bot.voice_clients[0]

        self.clients[ctx.guild.id] = voice_client

        filename = f"mp3s/{ctx.guild.id}.mp3"

        os.makedirs("mp3s", exist_ok=True)
        if os.path.exists(filename):
            os.remove(filename)

        await ctx.reply("on it")
        voice_client.play(await self.get_audio(query, filename, ctx))
        await ctx.reply("downloaded")

        while voice_client.is_playing() or voice_client.is_paused():
            await asyncio.sleep(1)

        await voice_client.disconnect()

    @commands.command(aliases=["pa"])
    async def pause(self, ctx: commands.Context):
        await ctx.reply("Paused")
        self.clients[ctx.guild.id].pause()

    @commands.command()
    async def stop(self, ctx: commands.Context):
        await ctx.reply("Stopped")
        self.clients[ctx.guild.id].stop()

    @staticmethod
    async def get_audio(query: str, filename: str, ctx: commands.Context) -> discord.FFmpegOpusAudio:
        options = {
            'format': 'bestaudio/best',
            'keepvideo': False,
            'outtmpl': filename,
            'noplaylist': True,
            'default_search': "ytsearch",
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'}]
        }

        with youtube_dl.YoutubeDL(options) as ydl:
            async with ctx.typing():
                ydl.download([query])

        return discord.FFmpegOpusAudio(filename, bitrate=256)


def setup(bot: commands.Bot):
    bot.add_cog(MusicPlayer(bot))

