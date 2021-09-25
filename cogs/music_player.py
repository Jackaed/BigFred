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

    @commands.command(aliases=["p"])
    async def play(self, ctx: commands.Context, *args):

        if len(args) == 0:
            await self.fred_functions.command_error(ctx, ["YouTube link"])
            return

        if ctx.message.author.voice is None:
            await self.fred_functions.custom_error(ctx, "User not in VC", "You need to be in a voice channel to use this command.")
            return

        user = ctx.message.author
        voice_channel = user.voice.channel
        voice_client = await voice_channel.connect()

        video_url = args[0] if args[0][0:4] == "http" else f"https://www.youtube.com/watch?v={args[0]}"

        filename = f"mp3s/{ctx.guild.id}.mp3"

        os.makedirs("mp3s", exist_ok=True)
        if os.path.exists(filename):
            os.remove(filename)

        voice_client.play(self.get_audio(video_url, filename))

        while voice_client.is_playing():
            await asyncio.sleep(1)

        await voice_client.disconnect()

    @staticmethod
    def get_audio(url: str, filename: str) -> discord.FFmpegOpusAudio:
        video_info = youtube_dl.YoutubeDL().extract_info(
            url=url, download=False
        )

        options = {
            'format': 'bestaudio/best',
            'keepvideo': False,
            'outtmpl': filename,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'}]
        }

        with youtube_dl.YoutubeDL(options) as ydl:
            ydl.download([video_info['webpage_url']])

        return discord.FFmpegOpusAudio(filename, bitrate=256)


def setup(bot: commands.Bot):
    bot.add_cog(MusicPlayer(bot))

