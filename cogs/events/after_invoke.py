import discord
from discord.ext import commands

import modules.APIs.tenor as tenorLib
import modules.helpers as helpers

class AfterInvoke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_command(self, ctx):
        pass
    
    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        pass
    
async def setup(bot):
    await bot.add_cog(AfterInvoke(bot))
