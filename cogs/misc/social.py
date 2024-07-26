import discord
from discord.ext import commands

import modules.APIs.tenor as tenorLib
import modules.helpers as helpers

class Social(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="bite",
        brief="command_brief_bite",
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
        brief="command_brief_boop",
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
        brief="command_brief_bonk",
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
    
    @commands.command(
        name="tickle",
        brief="command_brief_tickle",
        extras={"page": "main", "category":"social"}
    )
    async def tickle_command(self, ctx, target: discord.Member):
        embed = helpers.create_embed(ctx)
        if ctx.author == target:
            embed.title = f"{ctx.author.display_name} just started tickling themselves"
            embed.description = "wait i thought that was impossible?"
        else:
            embed.title = f"{ctx.author.display_name} started tickling {target.display_name} out of nowhere"
            embed.description = "teeheehehee"
        
        embed.set_image(url = tenorLib.getRandomGifLink("anime tickle", 30))
        await ctx.send(embed = embed)
    
    @commands.command(
        name="cuddle", aliases=["hug²"],
        brief="command_brief_cuddle",
        extras={"page": "main", "category":"social"}
    )
    async def cuddle_command(self, ctx, target: discord.Member):
        embed = helpers.create_embed(ctx)
        if ctx.author == target:
            embed.title = f"{ctx.author.display_name} is showing themselves some love"
            embed.description = ":3"
        else:
            embed.title = f"{ctx.author.display_name} took {target.display_name} and started cuddling them"
            embed.description = "awwweee"
        
        embed.set_image(url = tenorLib.getRandomGifLink("anime cuddle", 25))
        await ctx.send(embed = embed)
        
    @commands.command(
        name="hug",
        brief="command_brief_hug",
        extras={"page": "main", "category":"social"}
    )
    async def hug_command(self, ctx, target: discord.Member):
        embed = helpers.create_embed(ctx)
        if ctx.author == target:
            embed.title = f"{ctx.author.display_name} is showing themselves some love"
            embed.description = ":3"
        else:
            embed.title = f"{ctx.author.display_name} is hugging {target.display_name}"
            embed.description = "hugs! :)"
        
        embed.set_image(url = tenorLib.getRandomGifLink("anime hug", 25))
        await ctx.send(embed = embed)


async def setup(bot):
    await bot.add_cog(Social(bot))
