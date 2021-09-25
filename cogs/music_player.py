import asyncio
import discord
import os
from youtubesearchpython import VideosSearch
from discord.ext import commands
import youtube_dl
from cogs.fred_functions import FredFunctions


class MusicPlayer(commands.Cog):

    voice_client: discord.VoiceClient
    voice_channel: discord.VoiceChannel

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.fred_functions: FredFunctions = bot.get_cog("FredFunctions")
        self.voice_client = None
        self.voice_channel = None

    @commands.command(aliases=["p"])
    async def play(self, ctx: commands.Context, *args):

        if len(args) == 0:


            if self.voice_client and self.voice_client.is_paused():

                    self.voice_client.resume()
                    return

            video_url = "https://www.youtube.com/watch?v=SyimUCBIo6c"

        else:

            search = VideosSearch(" ".join(args), limit=1)
            video_url = search.result()['result'][0]['link']
            await self.fred_functions.command_error(ctx, ["YouTube link"])
            return

        if ctx.message.author.voice is None:
            await self.fred_functions.custom_error(ctx, "User not in VC",
                                                   "You need to be in a voice channel to use this command.")
            return

        user = ctx.message.author
        self.voice_channel = user.voice.channel
        self.voice_client = await self.voice_channel.connect()

        filename = f"mp3s/{ctx.guild.id}.mp3"

        os.makedirs("mp3s", exist_ok=True)
        if os.path.exists(filename):
            os.remove(filename)

        self.voice_client.play(self.get_audio(video_url, filename))

        while self.voice_client.is_playing() or self.voice_client.is_paused():
            await asyncio.sleep(1)

        await self.voice_client.disconnect()
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


    @commands.command(aliases=["pa"])
    async def pause(self, ctx: commands.Context):

        if not self.voice_client or not self.voice_client.is_playing():
            await self.fred_functions.custom_error(ctx, "Fred is not playing anything",
                                                   "Fred must be playing a song in order for it "
                                                   "to be paused you cretin.")
            return

        if self.voice_client.is_paused():
            await self.fred_functions.custom_error(ctx, "Song already paused", "The song is already paused, so it "
                                                                               "cannot be even more paused "
                                                                               "you absolute buffoon.")
            return

        self.voice_client.pause()

    @commands.command()
    async def stop(self, ctx: commands.Context):

        if not self.voice_client or (self.voice_client.is_paused and not self.voice_client.is_playing):
            await self.fred_functions.custom_error(ctx, "Nothing to stop", "There is no song currently playing or "
                                                                           "paused, so there is nothing to "
                                                                           "stop you imbecile.")
            return

        self.voice_client.stop()


def setup(bot: commands.Bot):
    bot.add_cog(MusicPlayer(bot))
