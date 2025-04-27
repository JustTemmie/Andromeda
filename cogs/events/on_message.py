import discord
from discord.ext import commands, tasks
from discord.errors import Forbidden
from discord.ext.commands import CommandNotFound, BadArgument, MissingRequiredArgument, CommandOnCooldown

class OnMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content in ["miku, say the thing", "miku say the thing"]:
            await message.channel.send(file=discord.File("assets/images/abortion.png"))


async def setup(bot):
    await bot.add_cog(OnMessage(bot))
