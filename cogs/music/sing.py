import discord
from discord.ext import commands
from discord import app_commands

from mutagen.mp3 import MP3
import asyncio

import hatsune_miku.helpers as helpers
import hatsune_miku.decorators as decorators


class Sing(commands.Cog):
    def __init__(self, miku):
        self.miku = miku
        self.data = {}

    async def sendNowPlayingEmbed(self, ctx):
        if ctx.guild.id not in self.data:
            await ctx.send("sorry, i'm not playing any songs within this server")
            return
        
        audio_data = MP3(self.data[ctx.guild.id]["song_path"])
        audio_duration = round(audio_data.info.length)
        
        embed = discord.Embed()
        try:
            embed.title = audio_data["TIT2"].text[0]
        except:  # noqa: E722
            embed.title = self.data[ctx.guild.id]["song_path"]
        embed.description = ""
        embed.colour = discord.Colour.from_str("#86cecb")
        # embed.set_author(name=audio_data["TIT2"].text[0], icon_url=ctx.me.display_avatar.url)
        embed.set_footer(
            text=f"Requested by {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url
        )
        
        embed.add_field(
            name = "Duration",
            value = f"{audio_duration // 60}m {audio_duration % 60}s"
        )
        embed.add_field(
            name = "Author",
            value = "Hatsune Miku"
        )

        await ctx.send(embed=embed)
        
    @commands.hybrid_command(name="sing", aliases=["play"])
    async def singCommand(self, ctx):
        if discord.utils.get(self.miku.voice_clients, guild=ctx.guild):
            await ctx.send("sorry, i'm already busy playing another banger in this server")
            return

        try:
            voice_channel = ctx.author.voice.channel
        
        except:
            await ctx.send("it doesn't seem like you're in a voice channel")
            return
            
        if voice_channel is not None:
            async def playSong():
                try:
                    # make sure there's actually usable data in the data dictionary
                    if ctx.guild.id not in self.data:
                        return
                    
                    song = helpers.getRandomSong()
                    self.data[ctx.guild.id]["song_path"] = song
                    
                    vc.play(
                        discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(song), 0.3),
                        after=lambda e: asyncio.run_coroutine_threadsafe(
                            playSong(), self.miku.loop
                        )
                    )
                    
                    await self.sendNowPlayingEmbed(ctx)
                
                except Exception as err:
                    # delete the data assocaited with this server
                    del self.data[ctx.guild.id]
                    await ctx.send(f"whoopsie, it looks like i encountered an error\n```{err}```")
            
            vc = await voice_channel.connect(self_deaf=True)
            self.data[ctx.guild.id] = {}
            
            await playSong()

    
    @commands.command(name="nowplaying", aliases=["now-playing", "np"])
    async def nowplayingCommand(self, ctx):
        await self.sendNowPlayingEmbed(ctx)

    @commands.command(name="psps")
    async def pspsCommand(self, ctx):
        voice_channel = ctx.author.voice.channel
        
        if voice_channel is not None:
            voice = discord.utils.get(self.miku.voice_clients, guild=ctx.guild)
            voice.pause()
            await voice.move_to(voice_channel)
            await asyncio.sleep(5)
            voice.resume()
        else:
            await ctx.send("it doesn't seem like you're in a voice channel")
    
    @commands.command(name="skip")
    async def skipCommand(self, ctx):
        # this stops the song, making the next song automatically start
        discord.utils.get(self.miku.voice_clients, guild=ctx.guild).stop()
    
    @commands.command(name="disconnect", aliases=["leave"])
    async def disconnectCommand(self, ctx):
        voice = discord.utils.get(self.miku.voice_clients, guild=ctx.guild)
        del self.data[ctx.guild.id]
        if voice:
            await voice.disconnect()
        else:
            await ctx.send("sorry, i don't seem to be in any voice channels at the moment")

async def setup(miku):
    await miku.add_cog(Sing(miku))
