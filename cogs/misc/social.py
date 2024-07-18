import discord
from discord.ext import commands

import modules.APIs.tenor as tenorLib
import modules.helpers as helpers

class Social(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="bite",
        description="Aumch",
        extras={"page": "main", "category":"social"}
    )
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
        description="bleep",
        extras={"page": "main", "category":"social"}
    )
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
        description="ouchie :(",
        extras={"page": "main", "category":"social"}
    )
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


async def setup(bot):
    await bot.add_cog(Social(bot))
