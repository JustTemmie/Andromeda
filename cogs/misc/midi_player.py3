import discord
from discord.ext import commands

import subprocess
import os

class MidiPlayer(commands.Cog):
    def __init__(self, miku):
        self.miku = miku

    @commands.command(name="midify")
    async def midify_command(self, ctx):
        await ctx.send("hi")
        os.(["timidity", "input.mid", "-Ow", "-o", "out.wav"])#, '--config-string=soundfont assets/misc/hatsune-miku-soundfont.sf2'])


async def setup(miku):
    await miku.add_cog(MidiPlayer(miku))
