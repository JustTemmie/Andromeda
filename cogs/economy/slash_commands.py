import discord
from discord.ext import commands
from discord import app_commands
import asyncio

if __name__ == "__main__":
    import sys
    sys.path.append(".")

import modules.localAPIs.database as DbLib
import cogs.economy.common as common
import config
from launcher import lang

class EconomyGroup(app_commands.Group):
    def __init__(self, bot: commands.Bot):
        super().__init__(name="economy", description="economy related commands")
        self.bot = bot
    
    @app_commands.command(name="testycommand")
    async def marry_slash_command(
        self, interaction: discord.Interaction
    ):
        await interaction.response.send_message("hello!!!!")

class SlashEconomyLoader(commands.Cog):
    def __init__(self, bot: commands.Bot):
        bot.tree.add_command(EconomyGroup(bot))

async def setup(bot):
    await bot.add_cog(SlashEconomyLoader(bot))