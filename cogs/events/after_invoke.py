import discord
from discord.ext import commands

import hatsune_miku.APIs.tenor as tenorLib
import hatsune_miku.helpers as helpers

class AfterInvoke(commands.Cog):
    def __init__(self, miku):
        self.miku = miku

    # @commands.Cog.listener()
    # async def on_command(self, ctx):
    #     pass
    
    # @commands.Cog.listener()
    # async def on_command_completion(self, ctx):
    #     pass
    
async def setup(miku):
    await miku.add_cog(AfterInvoke(miku))
