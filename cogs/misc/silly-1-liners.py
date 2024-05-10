import discord
from discord.ext import commands

import hatsune_miku.helpers as helpers

import hatsune_miku.APIs.tenor as tenorLib


class Silly(commands.Cog):
    def __init__(self, miku):
        self.miku = miku

    @commands.command(name="explode", aliases=["detonate", "dnace"])
    async def explode_command(self, ctx):
        await ctx.send("https://tenor.com/view/miku-hatsune-hatsune-miku-miku-explosion-explosion-gif-gif-26996455")
    
    @commands.hybrid_command(
        name="dance",
        description="Look at my moves!!")
    async def danceCommand(self, ctx):
        await ctx.send(tenorLib.getRandomGifLink("hatsune miku dancing", 10))


async def setup(miku):
    await miku.add_cog(Silly(miku))
