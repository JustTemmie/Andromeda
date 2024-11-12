import discord
from discord.ext import commands
from discord import app_commands

if __name__ == "__main__":
    import sys
    sys.path.append(".")

import config

from objects import lang
import cogs.economy.common.daily as daily

slash_economy_group = app_commands.Group(
    name="economy",
    description="economy commands",
    guild_ids=[1016777760305320036]
)

class SlashEconomyLoader(commands.Cog):
    def __init__(self, bot: commands.Bot):
        bot.tree.add_command(slash_economy_group)
        
        @slash_economy_group.command()
        async def hello(interaction: discord.Interaction):
            await interaction.response.send_message('Hello')

        @slash_economy_group.command(name="version")
        async def version(interaction: discord.Interaction):
            await interaction.response.send_message('This is an untested test version')

        @slash_economy_group.command(name="marry")
        async def marry_slash_command(interaction: discord.Interaction):
                await interaction.response.send_message("mrrp :3")
        
            
async def setup(bot):
    await bot.add_cog(SlashEconomyLoader(bot))