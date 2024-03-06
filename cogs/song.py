import discord
from discord.ext import commands
from discord.ext.commands import bot_has_permissions

import os
import random

import hatsune_miku.decorators as decorators
        
class Song(commands.Cog):
    def __init__(self, miku):
        self.miku = miku

    @commands.command(name="song")
    async def song(self, ctx):
        folder = "assets/music"
        files = os.listdir(folder)
        song = random.choice(files)
        
        await ctx.send(song, file=discord.File(f"{folder}/{song}"))
        
async def setup(miku):
    await miku.add_cog(Song(miku))
