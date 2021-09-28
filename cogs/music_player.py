import asyncio
import random
import time

import discord
import os
from discord.ext import commands
import youtube_dl
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import messages
from cogs.fred_functions import FredFunctions

try:
    with open(".client_secret") as f:
        file = f.readlines()
    client_secret = file[0].rstrip("\n")
    client_id = file[1].rstrip("\n")

except FileNotFoundError:
    raise FileNotFoundError("Could not find .client_secret file")

client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


class MusicPlayer(commands.Cog):

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.fred_functions: FredFunctions = bot.get_cog("FredFunctions")

        self.clients: {int: discord.VoiceClient} = {}
        self.song: {dict} = {}
        self.time: {dict} = {}

    @commands.command(aliases=["np", "current", "playing"])
    async def song(self, ctx: commands.Context):

        if ctx.message.author.voice is None:
            await self.fred_functions.custom_error(ctx, "User not in VC",
                                                   "You need to be in a voice channel to use this command.")
            return

        if ctx.guild.id not in self.clients:
            await self.fred_functions.custom_error(ctx, "Fred not playing",
                                                   "Fred is currently not playing any music.")
            return

        try:
            if ctx.guild.id in self.clients and self.clients[ctx.guild.id].is_paused():
                progress = int(time.time() - (
                            self.time[ctx.guild.id]["start"] + (time.time() - self.time[ctx.guild.id]["paused"])))
            else:
                progress = int(time.time() - self.time[ctx.guild.id]["start"])

            song = self.song[ctx.guild.id]
            duration = int(str(list(song["info_field"].split("\n"))[2]).strip("Duration: `seconds`"))

            embed = discord.Embed(title="Current Song",
                                  description=song["description"],
                                  colour=discord.Colour.purple())
            embed.set_image(url=song["url"])
            embed.set_footer(text=song["text"])

            info_field = song["info_field"] + \
                         "\n" + f"Progress: `{progress} seconds`" + \
                         "\n" + f"Persentage complete: `{int(progress / duration * 100)} %`"

            embed.add_field(name="Info", value=info_field)

            discord.Message = await ctx.reply(embed=embed)
        except FileNotFoundError:
            discord.Message = await ctx.reply(
                embed=discord.Embed(title="No Song playing", description="There is currently no song playing.",
                                    colour=discord.Colour.purple()))

    @commands.command(aliases=["p", "resume", "r"])
    async def play(self, ctx: commands.Context, *args):

        if ctx.message.author.voice is None:
            await self.fred_functions.custom_error(ctx, "User not in VC",
                                                   "You need to be in a voice channel to use this command.")
            return

        if ctx.guild.id in self.clients and self.clients[ctx.guild.id].is_paused():
            self.clients[ctx.guild.id].resume()
            self.time[ctx.guild.id]["start"] = self.time[ctx.guild.id]["start"] + (
                        time.time() - self.time[ctx.guild.id]["paused"])
            await ctx.reply("Resumed")
            return

        query = " ".join(args) if args else random.choice(messages.SONGS)

        if "https://open.spotify.com/track/" in query:
            query.strip("https://open.spotify.com/track/")
            spotify_info = spotify.track(query)
            query = f'{spotify_info["name"]} by {spotify_info["album"]["artists"][0]["name"]}'

        user = ctx.message.author
        voice_channel = user.voice.channel

        if ctx.guild.id in self.clients:
            voice_client = self.clients[ctx.guild.id]
        else:
            voice_client: discord.VoiceClient = await voice_channel.connect()
            self.clients[ctx.guild.id] = voice_client

        filename = f"mp3s/{ctx.guild.id}.mp3"

        os.makedirs("mp3s", exist_ok=True)
        if os.path.exists(filename):
            os.remove(filename)

        msg: discord.Message = await ctx.reply(
            embed=discord.Embed(title="Music Player", description="Downloading song...",
                                colour=discord.Colour.purple()))
        audio, info = self.get_audio(query, filename)
        voice_client.play(audio)

        info = info["entries"][0]

        embed = discord.Embed(title="Music Player",
                              description=f"Now Playing: `{info.get('track', info['title'])}`",
                              colour=discord.Colour.purple())
        embed.set_image(url=info['thumbnail'])
        embed.set_footer(text=f"https://www.youtube.com/watch?v={info['id']}")

        info_field = f"Album: `{info.get('album', 'none')}`\n" \
                     f"Artist: `{info.get('artist', 'none')}`\n" \
                     f"Duration: `{info.get('duration', -1)} seconds`"

        embed.add_field(name="Info", value=info_field)

        await msg.edit(embed=embed)

        self.song[ctx.guild.id] = {"description": f"Now Playing: `{info.get('track', info['title'])}`",
                                   "url": info['thumbnail'],
                                   "text": f"https://www.youtube.com/watch?v={info['id']}",
                                   "info_field": info_field}

        self.time[ctx.guild.id] = {"start": time.time(), "paused": 0.0}

        while voice_client.is_playing() or voice_client.is_paused():
            await asyncio.sleep(1)

        self.clients.pop(ctx.guild.id)
        self.time.pop(ctx.guild.id)
        self.song.pop(ctx.guild.id)
        await voice_client.disconnect()

    @commands.command(aliases=["pa"])
    async def pause(self, ctx: commands.Context):
        await ctx.reply("Paused")
        self.clients[ctx.guild.id].pause()
        self.time[ctx.guild.id]["paused"] = time.time()

    @commands.command()
    async def stop(self, ctx: commands.Context):
        await ctx.reply("Stopped")
        self.clients[ctx.guild.id].stop()

    @staticmethod
    def get_audio(query: str, filename: str) -> (discord.FFmpegOpusAudio, {}):
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
            info = ydl.extract_info(query, download=False)

            try:
                ydl.download([query])
            except youtube_dl.DownloadError:
                ydl.download(random.choice(messages.SONGS))

        return discord.FFmpegOpusAudio(filename, bitrate=64), info


def setup(bot: commands.Bot):
    bot.add_cog(MusicPlayer(bot))
