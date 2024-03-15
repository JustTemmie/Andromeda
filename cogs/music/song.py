import discord
from discord.ext import commands

import hatsune_miku.helpers as helpers

class Song(commands.Cog):
    def __init__(self, miku):
        self.miku = miku

    @commands.hybrid_command(
        name="song",
        description="I'll send one of my most popular songs")
    async def songCommand(self, ctx):
        song = helpers.getRandomSong()
        await ctx.send(song, file=discord.File(song))


async def setup(miku):
    await miku.add_cog(Song(miku))
