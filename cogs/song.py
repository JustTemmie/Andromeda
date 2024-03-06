import discord
from discord.ext import commands

import os
import random
import time

import hatsune_miku.helpers as helpers


class Song(commands.Cog):
    def __init__(self, miku):
        self.miku = miku

    @commands.command(name="song")
    async def songCommand(self, ctx):
        song = helpers.get_random_song()
        await ctx.send(song, file=discord.File(song))

    @commands.command(name="sing")
    async def singCommand(self, ctx):
        voice_channel = ctx.author.voice.channel
        if voice_channel is not None:
            song = helpers.get_random_song()
            vc = await voice_channel.connect(self_deaf=True)
            vc.play(discord.FFmpegPCMAudio(song))
            discord.FFmpegAudio.cleanup()
            while vc.is_playing():
                time.sleep(.1)
            await vc.disconnect()
        else:
            await ctx.send(str(ctx.author.name) + "is not in a channel.")


async def setup(miku):
    await miku.add_cog(Song(miku))
