import discord
from discord.ext import commands
from discord import app_commands

if __name__ == "__main__":
    import sys
    sys.path.append(".")

from objects import lang

class BOILERPLATE(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="explode", aliases=["detonate", "dnace"],
        brief="command_brief_CHANGEME",
        extras={"page": "main", "category":"undefined"}
    )
    async def explode_text_command(self, ctx: commands.Context):
        await ctx.send("https://tenor.com/view/bot-hatsune-hatsune-bot-bot-explosion-explosion-gif-gif-26996455")
    
    @app_commands.command(
        name="explode",
        description="whoppise, temmie forgor to change this"
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def explode_slash_command(
        self, intercation: discord.Interaction,
    ):
        await intercation.response.send_message("https://tenor.com/view/bot-hatsune-hatsune-bot-bot-explosion-explosion-gif-gif-26996455")


async def setup(bot):
    await bot.add_cog(BOILERPLATE(bot))
