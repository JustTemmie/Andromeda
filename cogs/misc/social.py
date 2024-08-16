import discord
from discord.ext import commands

import modules.APIs.tenor as tenorLib
import modules.helpers as helpers
from objects import lang

class Social(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def set_embed_content(self, embed, actionID, author, target):
        if target:
            embed.title = lang.tr(f"social_{actionID}_target_title", userID=author.id, user=author.display_name, target=target.display_name)
            embed.description = lang.tr(f"social_{actionID}_target_description", userID=author.id)
        else:
            embed.title = lang.tr(f"social_{actionID}_self_title", userID=author.id, user=author.display_name)
            embed.description = lang.tr(f"social_{actionID}_self_description", userID=author.id)


    @commands.command(
        name="bite",
        brief="command_brief_bite",
        extras={"page": "main", "category":"social"}
    )
    async def bite_command(self, ctx, target: discord.Member):
        embed = helpers.create_embed(ctx, user=target)
        self.set_embed_content(embed, "bite", ctx.author, target)

        embed.set_image(url = tenorLib.getRandomGifLink("anime bite", 10))
        await ctx.send(embed = embed)
    
    @commands.command(
        name="boop",
        brief="command_brief_boop",
        extras={"page": "main", "category":"social"}
    )
    async def boop_command(self, ctx, target: discord.Member):
        embed = helpers.create_embed(ctx, user=target)
        self.set_embed_content(embed, "boop", ctx.author, target)

        embed.set_image(url = tenorLib.getRandomGifLink("anime boop", 20))
        await ctx.send(embed = embed)
    
    @commands.command(
        name="bonk",
        brief="command_brief_bonk",
        extras={"page": "main", "category":"social"}
    )
    async def bonk_command(self, ctx, target: discord.Member):
        embed = helpers.create_embed(ctx, user=target)
        self.set_embed_content(embed, "bonk", ctx.author, target)

        embed.set_image(url = tenorLib.getRandomGifLink("anime bonk", 30))
        await ctx.send(embed = embed)
    
    @commands.command(
        name="tickle",
        brief="command_brief_tickle",
        extras={"page": "main", "category":"social"}
    )
    async def tickle_command(self, ctx, target: discord.Member):
        embed = helpers.create_embed(ctx, user=target)
        self.set_embed_content(embed, "tickle", ctx.author, target)

        embed.set_image(url = tenorLib.getRandomGifLink("anime tickle", 30))
        await ctx.send(embed = embed)
    
    @commands.command(
        name="cuddle", aliases=["hug²"],
        brief="command_brief_cuddle",
        extras={"page": "main", "category":"social"}
    )
    async def cuddle_command(self, ctx, target: discord.Member):
        embed = helpers.create_embed(ctx, user=target)
        self.set_embed_content(embed, "cuddle", ctx.author, target)

        embed.set_image(url = tenorLib.getRandomGifLink("anime cuddle", 25))
        await ctx.send(embed = embed)
        
    @commands.command(
        name="hug",
        brief="command_brief_hug",
        extras={"page": "main", "category":"social"}
    )
    async def hug_command(self, ctx, target: discord.Member):
        embed = helpers.create_embed(ctx, user=target)
        self.set_embed_content(embed, "hug", ctx.author, target)
        
        embed.set_image(url = tenorLib.getRandomGifLink("anime hug", 25))
        await ctx.send(embed = embed)


async def setup(bot):
    await bot.add_cog(Social(bot))
