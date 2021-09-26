import asyncio
import random

import discord
import os
from discord.ext import commands
import youtube_dl
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import messages
from cogs.fred_functions import FredFunctions

client_id =  "ab145034fa4e431ea3a94666038f3f1e"
client_secret = "97a896b65a3444e88a9e713cdee7248b"
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

class MusicPlayer(commands.Cog):

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.fred_functions: FredFunctions = bot.get_cog("FredFunctions")

        self.clients: {int: discord.VoiceClient} = {}

    @commands.command(aliases=["np", "current", "playing"])
    async def song(self, ctx: commands.Context, *args):
        if ctx.message.author.voice is None:
            await self.fred_functions.custom_error(ctx, "User not in VC",
                                                   "You need to be in a voice channel to use this command.")
            return

        try:
            id = str(ctx.guild.id)
            with open("Songs/info." + id) as f:
                info = f.readlines()

            embed = discord.Embed(title="Current Song", description=info[0].rstrip("\n"),
                                  colour=discord.Colour.purple())
            embed.set_image(url=info[1].rstrip("\n"))
            embed.set_footer(text=info[2].rstrip("\n"))

            info_field = info[3].rstrip("\n") + "\n" + info[4].rstrip("\n") + "\n" + info[5].rstrip("\n")

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
            await ctx.reply("Resumed")
            return

        query = " ".join(args) if args else random.choice(messages.SONGS)

        if "https://open.spotify.com/track/" in query:
            query.strip("https://open.spotify.com/track/")
            spotify_info = spotify.track(query)
            for i in spotify_info["artists"]:
                print(i)
            query = f'{spotify_info["name"]} by {spotify_info["album"]["artists"][0]["name"]}'
            print(query)


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
            try:
                os.remove(filename)
            except PermissionError:
                await ctx.reply(embed=discord.Embed(title="Music Player", description="A song is already playing.", colour=discord.Colour.purple()))
                return

        msg: discord.Message = await ctx.reply(
            embed=discord.Embed(title="Music Player", description="Downloading song...",
                                colour=discord.Colour.purple()))
        audio, info = self.get_audio(query, filename)

        voice_client.play(audio)

        try:
            entries = info["entries"][0]
        except KeyError:
            entries = {}

            print(info)

        embed = discord.Embed(title="Music Player",
                              description=f"Now Playing: `{entries.get('track', entries['title'])}`",
                              colour=discord.Colour.purple())
        embed.set_image(url=entries.get('thumbnail', 'https://cdn.discordapp.com/icons/728673767559135323/cc76b1f50106f69ceb94d530bc8d3a75.webp?size=1024'))
        embed.set_footer(text=f"https://www.youtube.com/watch?v={info['id']}")

        info_field = f"Album: `{entries.get('album', '-')}`\n" \
                     f"Artist: `{entries.get('artist', '-')}`\n" \
                     f"Duration: `{entries.get('duration', '-')} seconds`"

        embed.add_field(name="Info", value=info_field)

        await msg.edit(embed=embed)

        os.makedirs("Songs", exist_ok=True)
        id = str(ctx.guild.id)
        f = open("Songs/info." + id, "w")
        f.write(f"Now Playing: `{info.get('track', info['title'])}`" + "\n" +
                info['thumbnail'] + "\n" +
                f"https://www.youtube.com/watch?v={info['id']}" + "\n" +
                f"Album: `{info.get('album', 'none')}`\n" \
                f"Artist: `{info.get('artist', 'none')}`\n" \
                f"Duration: `{info.get('duration', -1)} seconds`")
        f.close()

        while voice_client.is_playing() or voice_client.is_paused():
            await asyncio.sleep(1)

        if ctx.guild.id in self.clients:
            self.clients.pop(ctx.guild.id)
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
