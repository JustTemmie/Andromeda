from discord.ext import commands

import os

def is_host_owner():
    async def predicate(ctx):
        if ctx.author.id in ctx.bot.custom_data["HOST_OWNERS"]:
            return True
        else:
            await ctx.send(f"hey, you're not responsible for {os.uname()[1]}")
            return False
        
    return commands.check(predicate)