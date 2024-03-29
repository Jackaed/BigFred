import asyncio
import time
from typing import Dict, List, Union
import random
import os

import youtube_dl
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import discord
from discord.ext import commands

import messages
import secrets
from cogs.fred_functions import FredFunctions


class Song:
    def __init__(self):
        self.status_message: Union[discord.Message, None] = None

        self.id: str = ""
        self.title: str = "Not Found"

        self.album: str = "Not Found"
        self.track: str = "Not Found"
        self.artist: str = "Not Found"
        self.thumbnail_url: str = "https://cdn.discordapp.com/icons/728673767559135323/cc76b1f50106f69ceb94d530bc8d3a75.webp"

        self.duration: int = 0
        self.progress: int = 0

        self.playing: bool = False
        self.downloaded: bool = False
        self.audio: Union[discord.FFmpegOpusAudio, None] = None
        self.file: str = ""

    @property
    def embed(self) -> discord.Embed:
        embed = discord.Embed(colour=discord.Colour.purple())

        embed.title = "Music Player"

        embed.add_field(name="Song Info", value=f"Album: `{self.album}`\n"
                                                f"Track: `{self.track}`\n"
                                                f"Artist: `{self.artist}`\n"
                                                f"Duration: `{self.duration} seconds`")
        embed.set_image(url=self.thumbnail_url)
        embed.set_footer(text=f"https://www.youtube.com/watch?v={self.id}")

        if self.playing:
            embed.description = f"Now Playing: `{self.title}`\n" \
                                f"Status: `Playing`\n" \
                                f"Playing for: `{round(self.progress)} seconds ({round(self.progress / self.duration * 100)}%)`"
        else:
            embed.description = f"Name: `{self.title}`\n" \
                                f"Status: `{'Downloaded' if self.downloaded else 'Waiting to download'}`"

        return embed

    def download(self):
        options = MusicPlayer.options
        options["outtmpl"] = self.file

        with youtube_dl.YoutubeDL(options) as ydl:
            ydl.download([f"https://www.youtube.com/watch?v={self.id}"])

        self.downloaded = True

        self.audio = discord.FFmpegOpusAudio(self.file, bitrate=64)


class MusicPlayer(commands.Cog):
    queue: Dict[int, List[Song]]
    clients: Dict[int, discord.VoiceClient]

    client_credentials_manager = SpotifyClientCredentials(client_id=secrets.SPOTIFY_ID,
                                                          client_secret=secrets.SPOTIFY_SECRET)
    spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    options = {
        "format": "worstaudio",
        "keepvideo": False,
        "outtmpl": "tmp.mp3",
        "noplaylist": True,
        "default_search": "ytsearch",
        "verbose": False,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "64"}]
    }

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.fred_functions: FredFunctions = bot.get_cog("FredFunctions")

        self.clients: {int: discord.VoiceClient} = {}
        self.queue: {int: [Song]} = {}

        self.downloads = 0
        self.max_downloads = 5
        self.min_downloads = 2

        os.makedirs("mp3s", exist_ok=True)
        for f in os.listdir("mp3s"):
            os.remove("mp3s/" + f)

    @commands.command(aliases=["np", "current"])
    async def playing(self, ctx: commands.Context):
        if ctx.guild.id not in self.clients or len(self.queue[ctx.guild.id]) == 0:
            await self.fred_functions.custom_error(ctx, "Fred not playing",
                                                   "Fred is currently not playing any music.")
            return

        discord.Message = await ctx.reply(embed=self.queue[ctx.guild.id][0].embed)

    @commands.command(aliases=["next", "qu", "queue"])
    async def view_queue(self, ctx: commands.Context):
        if ctx.guild.id not in self.queue or len(self.queue[ctx.guild.id]) == 0:
            await self.fred_functions.custom_error(ctx, "Fred not playing",
                                                   "Fred is currently not playing any music.")
            return

        embed = discord.Embed(title="Music Player", colour=discord.Colour.purple())
        embed.description = f"Length: {len(self.queue[ctx.message.guild.id])}\n"

        for i in range(min(len(self.queue[ctx.message.guild.id]), 11)):
            song = self.queue[ctx.message.guild.id][i]
            embed.description += f"{i}. {song.title}\n"

        await ctx.reply(embed=embed)

    @commands.command(aliases=["p", "resume", "r"])
    async def play(self, ctx: commands.Context, *args):

        if ctx.message.author.voice is None:
            await self.fred_functions.custom_error(ctx, "User not in VC",
                                                   "You need to be in a voice channel to use this command.")
            return

        if ctx.guild.id in self.clients and self.clients[ctx.guild.id].is_paused():
            self.clients[ctx.guild.id].resume()

            await ctx.reply("Resumed")
            return

        if ctx.guild.id not in self.queue:
            self.queue[ctx.guild.id] = []

        query = " ".join(args) if args else random.choice(messages.SONGS)

        if "https://open.spotify.com/track/" in query:
            query.strip("https://open.spotify.com/track/")
            spotify_info = self.spotify.track(query)
            query = f'{spotify_info["name"]} by {spotify_info["album"]["artists"][0]["name"]}'

        user = ctx.message.author
        voice_channel = user.voice.channel

        if ctx.guild.id in self.clients:
            voice_client = self.clients[ctx.guild.id]
        else:
            voice_client: discord.VoiceClient = await voice_channel.connect()
            self.clients[ctx.guild.id] = voice_client

        song = self.get_song(query)
        song.message = await ctx.reply(embed=song.embed)
        self.queue[ctx.guild.id].append(song)

        while voice_client.is_playing() or self.queue[ctx.guild.id].index(song) != 0:
            await song.message.edit(embed=song.embed)

            if self.downloads < self.min_downloads and self.downloads < self.max_downloads:
                song.download()
                self.downloads += 1

            await asyncio.sleep(1)

        if not song.audio:
            song.download()

        voice_client.play(self.queue[ctx.guild.id][0].audio)
        song.playing = True

        while voice_client.is_playing() or voice_client.is_paused():
            delay = 1

            if song.playing:
                self.queue[ctx.guild.id][0].progress += delay
                await song.message.edit(embed=song.embed)

            await asyncio.sleep(delay)

        self.queue[ctx.guild.id][0].progress = self.queue[ctx.guild.id][0].duration
        await song.message.edit(embed=song.embed)

        voice_client.stop()

        while True:
            try:
                os.remove(song.file)
                self.downloads -= 1
                break
            except PermissionError:
                await asyncio.sleep(1)
            except FileNotFoundError:
                self.downloads -= 1
                break

        if song in self.queue[ctx.guild.id]:
            self.queue[ctx.guild.id].remove(song)

        if ctx.guild.id in self.clients and len(self.queue[ctx.guild.id]) == 0:
            voice_client = self.clients[ctx.guild.id]
            await voice_client.disconnect()
            self.clients.pop(ctx.guild.id)

    @commands.command(aliases=["pa"])
    async def pause(self, ctx: commands.Context):
        if ctx.message.author.voice is None:
            await self.fred_functions.custom_error(ctx, "User not in VC",
                                                   "You need to be in a voice channel to use this command.")
            return

        self.clients[ctx.guild.id].pause()

        await ctx.reply("Paused")

    @commands.command()
    async def stop(self, ctx: commands.Context):
        if ctx.message.author.voice is None:
            await self.fred_functions.custom_error(ctx, "User not in VC",
                                                   "You need to be in a voice channel to use this command.")
            return
        await ctx.reply("Stopped")
        self.queue[ctx.guild.id] = []
        self.clients[ctx.guild.id].stop()

    @commands.command()
    async def clear(self, ctx: commands.Context):
        self.queue[ctx.guild.id].clear()

        await ctx.reply(embed=discord.Embed(title="Clear",
                                            colour=discord.Colour.purple(),
                                            description="Queue cleared"))

    @commands.command(aliases=["pop"])
    async def remove(self, ctx: commands.Context, position: int = -1):
        if ctx.message.author.voice is None:
            await self.fred_functions.custom_error(ctx, "User not in VC",
                                                   "You need to be in a voice channel to use this command.")
            return

        if len(self.queue[ctx.guild.id]) == 0:
            await self.fred_functions.custom_error(ctx, "Cannot remove song",
                                                   "There must be songs in the queue for you to remove one.")
            return

        self.queue[ctx.guild.id].pop(position)
        await ctx.reply(embed=discord.Embed(title="Remove",
                                            colour=discord.Colour.purple(),
                                            description=f"Removed song at position {position}"))

    @commands.command()
    async def skip(self, ctx: commands.Context):
        if ctx.message.author.voice is None:
            await self.fred_functions.custom_error(ctx, "User not in VC",
                                                   "You need to be in a voice channel to use this command.")
            return

        await ctx.reply("Skipped")

        self.clients[ctx.guild.id].stop()

    @staticmethod
    def get_song(query: str) -> Song:
        with youtube_dl.YoutubeDL(MusicPlayer.options) as ydl:
            info = ydl.extract_info(query, download=False)

        song = Song()

        if "entries" in info:
            info = info["entries"][0]

        song.id = info.get("id", song.id)
        song.title = info.get("title", song.title)

        song.album = info.get("album", song.album)
        song.track = info.get("track", song.track)
        song.artist = info.get("artist", song.artist)
        song.thumbnail_url = info.get("thumbnail", song.thumbnail_url)

        song.duration = info.get("duration", song.duration)

        song.file = f"mp3s/{song.id}.mp3"

        return song


def setup(bot: commands.Bot):
    bot.add_cog(MusicPlayer(bot))
