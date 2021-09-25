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
            await self.fred_functions.command_error(ctx, ["@user|name", "message"])
            return

        if ctx.message.author.voice is None:
            await self.fred_functions.custom_error(ctx, "User not in VC", "You need to be in a voice channel to use this command.")
            return

        user = ctx.message.author
        voice_channel = user.voice.channel
        voice_client = await voice_channel.connect()

        video_url = args[0]
        video_info = youtube_dl.YoutubeDL().extract_info(
            url=video_url, download=False
        )
        filename = "tmp.wav"
        options = {
            'format': 'bestaudio/best',
            'keepvideo': False,
            'outtmpl': filename,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',                'preferredcodec': 'mp3',
                'preferredquality': '192'}]
        }

        with youtube_dl.YoutubeDL(options) as ydl:
            ydl.download([video_info['webpage_url']])

        audio = discord.FFmpegOpusAudio("tmp.mp3", bitrate=256)
        voice_client.play(audio)

        while voice_client.is_playing():
            await asyncio.sleep(1)

        os.remove("tmp.mp3")
        await voice_client.disconnect()



def setup(bot: commands.Bot):
    bot.add_cog(MusicPlayer(bot))
   
