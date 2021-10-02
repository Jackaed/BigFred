import asyncio
from typing import Dict, Any, List

import discord
from discord.ext import commands

import youtube_dl
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import random
import time
import os

import messages
import secrets
from cogs.fred_functions import FredFunctions


class Song:
    def __init__(self):
        self.id: str = ""
        self.title: str = "Not Found"

        self.artist: str = "Not Found"
        self.album: str = "Not Found"
        self.thumbnail_url: str = "https://cdn.discordapp.com/icons/728673767559135323/cc76b1f50106f69ceb94d530bc8d3a75.webp"

        self.duration: int = 0
        self.progress: int = 0
        self.playing_since: int = 0

    @property
    def embed(self) -> discord.Embed:
        embed = discord.Embed(colour=discord.Colour.purple())

        embed.title = "Music Player"
        embed.description = f"Now Playing: `{self.title}`\n" \
                            f"Playing for: `{round(self.progress)} seconds ({round(self.progress / self.duration * 100)}%)`"
        embed.add_field(name="Song Info", value=f"Album: `{self.album}`\n"
                                                f"Artist: `{self.artist}`\n"
                                                f"Duration: `{self.duration} seconds`")
        embed.set_image(url=self.thumbnail_url)
        embed.set_footer(text=f"https://www.youtube.com/watch?v={self.id}")

        return embed


class MusicPlayer(commands.Cog):
    queue: Dict[int, List[Song]]

    client_credentials_manager = SpotifyClientCredentials(client_id=secrets.SPOTIFY_ID, client_secret=secrets.SPOTIFY_SECRET)
    spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.fred_functions: FredFunctions = bot.get_cog("FredFunctions")

        self.clients: {int: discord.VoiceClient} = {}
        self.queue: {int: [Song]} = {}

    @commands.command(aliases=["np", "current"])
    async def playing(self, ctx: commands.Context):
        if ctx.guild.id not in self.clients:
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

        # queue = list(self.queue[ctx.guild.id])
        # queue[0] = f"\nNow playing: `{queue[0]}`"
        #
        # for i in range(1, len(queue)):
        #     queue[i] = f"\n{i}: `{queue[i]}`"
        #
        # queue.insert(1, "\nUp next:")
        #
        # queue = "".join(queue)
        # embed = discord.Embed(title="Queue",
        #                       colour=discord.Colour.purple(),
        #                       description=queue)

        await ctx.reply("unfortunatley this command was programmed in a horrific manner")

    @commands.command(aliases=["p", "resume", "r"])
    async def play(self, ctx: commands.Context, *args):

        if ctx.message.author.voice is None:
            await self.fred_functions.custom_error(ctx, "User not in VC",
                                                   "You need to be in a voice channel to use this command.")
            return

        if ctx.guild.id in self.clients and self.clients[ctx.guild.id].is_paused():
            self.clients[ctx.guild.id].resume()
            self.queue[ctx.guild.id][0].playing_since = time.time()

            await ctx.reply("Resumed")
            return

        if ctx.guild.id not in self.queue:
            self.queue[ctx.guild.id] = []

        query = " ".join(args) if args else random.choice(messages.SONGS)

        if ctx.guild.id in self.clients and self.clients[ctx.guild.id].is_playing():
            discord.Message = await ctx.reply(
                embed=discord.Embed(title="Song Added", description="Song has been added to the queue",
                                    colour=discord.Colour.purple()))
            return

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

        filename = f"mp3s/{ctx.guild.id}.mp3"

        os.makedirs("mp3s", exist_ok=True)
        if os.path.exists(filename):
            os.remove(filename)

        msg: discord.Message = await ctx.reply(embed=discord.Embed(title="Music Player",
                                                                   description="Downloading song...",
                                                                   colour=discord.Colour.purple()))

        audio, info = self.get_audio(query, filename)
        song = self.extract_song(info)
        self.queue[ctx.guild.id].append(song)

        voice_client.play(audio)
        song.playing_since = time.time()

        await msg.edit(embed=song.embed)

        while voice_client.is_playing() or voice_client.is_paused():
            if voice_client.is_playing():
                self.queue[ctx.guild.id][0].progress = time.time() - song.playing_since
            await asyncio.sleep(1)

        if len(self.queue[ctx.guild.id]) > 0:
            self.queue[ctx.guild.id].pop(0)

        if ctx.guild.id in self.clients:
            voice_client = self.clients[ctx.guild.id]
            await voice_client.disconnect()

    @commands.command(aliases=["pa"])
    async def pause(self, ctx: commands.Context):
        if ctx.message.author.voice is None:
            await self.fred_functions.custom_error(ctx, "User not in VC",
                                                   "You need to be in a voice channel to use this command.")
            return
        await ctx.reply("Paused")
        self.clients[ctx.guild.id].pause()
        self.time[ctx.guild.id]["paused"] = time.time()

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
    async def insert(self, ctx: commands.Context, *args):
        if ctx.message.author.voice is None:
            await self.fred_functions.custom_error(ctx, "User not in VC",
                                                   "You need to be in a voice channel to use this command.")
            return

        try:
            int(args[0])
        except ValueError:
            await self.fred_functions.custom_error(ctx, "Cannot add song",
                                                   "A position in the queue must be supplyed in order to add a song.")
            return

        pos = int(args[0])
        qurey = " ".join(args).lstrip(str(pos))

        if not isinstance(qurey, str):
            await self.fred_functions.custom_error(ctx, "Cannot add song",
                                                   "A song must be supplyed in order to add a song.")
            return

        if len(self.queue[ctx.guild.id]) < 1:
            await self.fred_functions.custom_error(ctx, "Cannot remove song",
                                                   "There must be songs in the queue for you to remove one.")
            return

        self.queue[ctx.guild.id].insert(pos, qurey)
        await ctx.reply(embed=discord.Embed(title="Pop",
                                            colour=discord.Colour.purple(),
                                            description=f"addded song {qurey}"))

    @commands.command()
    async def clear(self, ctx: commands.Context):
        queue = self.queue[ctx.guild.id]

        for i in range(1, len(queue)):
            queue.pop(i)

        await ctx.reply(embed=discord.Embed(title="Clear",
                                            colour=discord.Colour.purple(),
                                            description="Queue cleared"))

    @commands.command()
    async def pop(self, ctx: commands.Context, *args):
        if ctx.message.author.voice is None:
            await self.fred_functions.custom_error(ctx, "User not in VC",
                                                   "You need to be in a voice channel to use this command.")
            return

        try:
            int(args[0])
        except ValueError:
            await self.fred_functions.custom_error(ctx, "Cannot add song",
                                                   "A position in the queue must be supplyed in order to remove a song.")
            return

        pos = int(args[0])

        if len(self.queue[ctx.guild.id]) < 1:
            await self.fred_functions.custom_error(ctx, "Cannot remove song",
                                                   "There must be songs in the queue for you to remove one.")
            return
        self.queue[ctx.guild.id].pop(pos)
        await ctx.reply(embed=discord.Embed(title="Pop",
                                            colour=discord.Colour.purple(),
                                            description=f"Removed song at position {args[0]}"))

    @commands.command()
    async def skip(self, ctx: commands.Context):
        if ctx.message.author.voice is None:
            await self.fred_functions.custom_error(ctx, "User not in VC",
                                                   "You need to be in a voice channel to use this command.")
            return
        await ctx.reply("Skipped")
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

    @staticmethod
    def extract_song(info: dict) -> Song:
        song = Song()

        if "entries" in info:
            info = info["entries"][0]

        song.id = info.get("id", song.id)
        song.title = info.get("title", song.title)

        song.artist = info.get("artist", song.artist)
        song.album = info.get("album", song.album)
        song.thumbnail_url = info.get("thumbnail", song.thumbnail_url)

        song.duration = info.get("duration", song.duration)

        return song


def setup(bot: commands.Bot):
    bot.add_cog(MusicPlayer(bot))
