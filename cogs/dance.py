from discord.ext import commands

import hatsune_miku.APIs.tenor as tenorLib

class Dance(commands.Cog):
    def __init__(self, miku):
        self.miku = miku

    @commands.hybrid_command(
        name="dance",
        description="Look at my moves!!")
    async def danceCommand(self, ctx):
        await ctx.send(tenorLib.getRandomGifLink("hatsune miku dancing", 10))


async def setup(miku):
    await miku.add_cog(Dance(miku))
