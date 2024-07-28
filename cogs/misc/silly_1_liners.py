import discord
from discord.ext import commands
from discord import app_commands

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
    
    @app_commands.command(
        name="dance",
        description="command_brief_dance"
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def dance_slash_command(self, ctx):
        await ctx.send(tenorLib.getRandomGifLink("hatsune miku dancing", 10))
        
    @commands.command(
        name="dance",
        brief="command_brief_dance",
        extras={"page": "main", "category":"silly"}
    )
    async def dance_command(self, ctx):
        await ctx.send(tenorLib.getRandomGifLink("hatsune miku dancing", 10))


async def setup(bot):
    await bot.add_cog(Silly(bot))
