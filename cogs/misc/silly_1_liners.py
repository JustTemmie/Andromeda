import discord
from discord.ext import commands

import time
import random

import modules.helpers as helpers
import modules.APIs.tenor as tenorLib


class Silly(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="explode", aliases=["detonate", "dnace"],
        extras={"page": "main", "category":"silly"}
    )
    async def explode_command(self, ctx):
        await ctx.send("https://tenor.com/view/miku-hatsune-hatsune-miku-miku-explosion-explosion-gif-gif-26996455")
    
    @commands.hybrid_command(
        name="dance",
        description="Look at my moves!!",
        extras={"page": "main", "category":"silly"}
    )
    async def danceCommand(self, ctx):
        await ctx.send(tenorLib.getRandomGifLink("hatsune miku dancing", 10))

    @commands.command(name="save", aliases=["sav"], hidden=True)
    async def save_command(self, ctx):
        msg = await ctx.reply("saving...")
        time.sleep(2)
        if random.random() > 0.95:
            await msg.reply("error: could not save file")
        else:
            await msg.reply("save file updated succesful")


async def setup(bot):
    await bot.add_cog(Silly(bot))
