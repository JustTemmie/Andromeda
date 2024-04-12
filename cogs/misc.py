import discord
from discord.ext import commands

import hatsune_miku.helpers as helpers

class Misc(commands.Cog):
    def __init__(self, miku):
        self.miku = miku

    @commands.command(name="explode")
    async def explodeCommand(self, ctx):
        await ctx.send("boom")


async def setup(miku):
    await miku.add_cog(Misc(miku))
