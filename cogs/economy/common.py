import discord
from discord.ext import commands
from discord import app_commands
import asyncio

if __name__ == "__main__":
    import sys
    sys.path.append(".")

import modules.localAPIs.database as DbLib
import settings
from launcher import lang

async def econonmy_daily_command(userID) -> str:
    # DbLib.economy_database.
    return settings.emojis.coin

async def setup(bot):
    pass