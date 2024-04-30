from discord.ext import commands

import hatsune_miku.APIs.tenor as tenorLib
import hatsune_miku.helpers as helpers

class Actions(commands.Cog):
    def __init__(self, miku):
        self.miku = miku

    @commands.hybrid_command(
        name="bite",
        description="Aumch")
    async def danceCommand(self, ctx):
        embed = helpers.create_embed(ctx)
        embed.title = "yum"
        
        embed.set_image(url = tenorLib.getRandomGifLink("anime bite", 25))
        
        await ctx.send(embed = embed)


async def setup(miku):
    await miku.add_cog(Actions(miku))
