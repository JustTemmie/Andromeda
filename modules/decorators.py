from discord.ext import commands

import os
import time

import functools

def is_host_owner():
    async def predicate(ctx) -> bool:
        if not ctx.author.id in ctx.bot.config["HOST_OWNERS"]:
            raise commands.NotOwner(f"You are not responsible for {os.uname()[1]}")
        else:
            return True
        
    return commands.check(predicate)

def command():
    async def predicate(ctx):
        # Define your cog class
        class MyCog(commands.Cog):
            def __init__(self, bot):
                self.bot = bot

            @commands.command(name='my_command', help='My custom command')
            async def my_command(self, ctx, arg):
                await ctx.send(f"You entered: {arg}")

        # Instantiate the cog
        my_cog = MyCog(ctx.bot)

        # Add the cog to the bot
        await ctx.bot.add_cog(my_cog)

        if ctx.author.id in ctx.bot.config["HOST_OWNERS"]:
            return True
        else:
            await ctx.send(f"hey, you're not responsible for {os.uname()[1]}")
            return False
        
    return commands.check(predicate)

# a wrapper for funcstools.lru_cache() that only holds data for x seconds
def time_cache(maxAgeSeconds, maxSize=128):
    def _decorator(func):
        @functools.lru_cache(maxsize=maxSize)
        def _new(*args, __time_salt, **kwargs):
            return func(*args, **kwargs)

        @functools.wraps(func)
        def _wrapped(*args, **kwargs):
            return _new(*args, **kwargs, __time_salt=int(time.time() / maxAgeSeconds))

        return _wrapped

    return _decorator