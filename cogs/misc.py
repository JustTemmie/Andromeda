import discord
from discord.ext import commands

import hatsune_miku.helpers as helpers

import hatsune_miku.APIs.tenor as tenorLib


class Misc(commands.Cog):
    def __init__(self, miku):
        self.miku = miku

    @commands.command(name="explode", aliases=["detonate", "dnace"])
    async def explodeCommand(self, ctx):
        await ctx.send("https://tenor.com/view/miku-hatsune-hatsune-miku-miku-explosion-explosion-gif-gif-26996455")


async def setup(miku):
    await miku.add_cog(Misc(miku))
