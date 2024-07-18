import discord
from discord.ext import commands

import modules.helpers as helpers
import modules.database as DbLib
import modules.APIs.tenor as tenorLib


class BOILERPLATE(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="explode", aliases=["detonate", "dnace"],
        brief="a brief description of the command, i probably forgot to change this, whoopsie",
        extras={"page": "main", "category":"undefined"}
    )
    async def explode_command(self, ctx: commands.Context):
        await ctx.send("https://tenor.com/view/bot-hatsune-hatsune-bot-bot-explosion-explosion-gif-gif-26996455")


async def setup(bot):
    await bot.add_cog(BOILERPLATE(bot))
