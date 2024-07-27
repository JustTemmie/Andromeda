import discord
from discord.ext import commands
from discord import app_commands
import asyncio

if __name__ == "__main__":
    import sys
    sys.path.append(".")

import modules.localAPIs.database as DbLib
import cogs.economy.common as common
from launcher import lang

class EconomyText(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.command("hi")
    async def command_hi(self, ctx):
        await ctx.send(await common.econonmy_daily_command(ctx.author.id))
    
    
async def setup(bot):
    await bot.add_cog(EconomyText(bot))