import discord
from discord.ext import commands

import hatsune_miku.APIs.tenor as tenorLib
import hatsune_miku.helpers as helpers

class Actions(commands.Cog):
    def __init__(self, miku):
        self.miku = miku

    @commands.command(
        name="bite",
        description="Aumch")
    async def bite_command(self, ctx, target: discord.Member):
        embed = helpers.create_embed(ctx)
        if ctx.author == target:
            embed.title = f"{ctx.author.display_name} just bit themselves"
            embed.description = "i don't think this is normal, even for a vampire"
        else:
            embed.title = f"{ctx.author.display_name} just bit {target.display_name}"
            embed.description = "rawr >:3"
        
        embed.set_image(url = tenorLib.getRandomGifLink("anime bite", 10))
        await ctx.send(embed = embed)
    
    @commands.command(
        name="boop",
        description="bleep")
    async def boop_command(self, ctx, target: discord.Member):
        embed = helpers.create_embed(ctx)
        if ctx.author == target:
            embed.title = f"{ctx.author.display_name} just booped themselves"
            embed.description = "bleep"
        else:
            embed.title = f"{ctx.author.display_name} just booped {target.display_name}"
            embed.description = "*boop*"
        
        embed.set_image(url = tenorLib.getRandomGifLink("anime boop", 20))
        await ctx.send(embed = embed)
    
    @commands.command(
        name="bonk",
        description="ouchie :(")
    async def bonk_command(self, ctx, target: discord.Member):
        embed = helpers.create_embed(ctx)
        if ctx.author == target:
            embed.title = f"{ctx.author.display_name} just bonked themselves"
            embed.description = "alright, sure"
        else:
            embed.title = f"{ctx.author.display_name} just bonked {target.display_name}"
            embed.description = "youch"
        
        embed.set_image(url = tenorLib.getRandomGifLink("anime bonk", 30))
        await ctx.send(embed = embed)


async def setup(miku):
    await miku.add_cog(Actions(miku))
