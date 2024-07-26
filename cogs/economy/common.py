import discord
from discord.ext import commands
from discord import app_commands
import asyncio

if __name__ == "__main__":
    import sys
    sys.path.append(".")

import modules.localAPIs.database as DbLib
from launcher import lang

async def setup(bot):
    pass