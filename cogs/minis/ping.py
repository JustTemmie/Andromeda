import discord
from discord.ext import commands
from discord import app_commands

from time import perf_counter

if __name__ == "__main__":
    import sys
    sys.path.append(".")

class Ping(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="ping",
        brief="measure my latency",
        extras={"page": "main", "category":"undefined"}
    )
    async def ping_text_command(self, ctx: commands.Context):
        start = perf_counter()
        msg = await self.bot.lang.tr_send(ctx, "ping_command_latency_check")
        end = perf_counter()
        msg_content = self.bot.lang.tr(
            "ping_command_latency_response",
            discord_latency=round(self.bot.latency * 1000),
            bot_latency=round((end - start) * 1000)
        )
        await msg.edit(content=msg_content)

    @app_commands.command(
        name="ping",
        description="check my latency",
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    async def ping_slash_command(self, interaction: discord.Interaction):
        start = perf_counter()
        await interaction.response.send_message(self.bot.lang.tr("ping_command_latency_check", interaction=interaction))
        end = perf_counter()
        msg_content = self.bot.lang.tr(
            "ping_command_latency_response",
            interaction=interaction,
            discord_latency=round(self.bot.latency * 1000),
            bot_latency=round((end - start) * 1000)
        )
        await interaction.edit_original_response(content=msg_content)

async def setup(bot):
    await bot.add_cog(Ping(bot))
