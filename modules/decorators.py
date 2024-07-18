from discord.ext import commands

import os


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