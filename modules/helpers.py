import discord
from discord.ext import commands

import os
import random
import math

def getProgressBar(current, max, width = 20):
    percent = int(width * current / max)
    bar = "█" * percent + "░" * (width - percent)

    return bar

# user still needs to set the title, description, and fields
def create_embed(ctx: commands.Context, user = None):
    if user == None:
        user = ctx.author
    
    embed = discord.Embed()
    embed.colour = user.colour if user.colour != discord.Colour.default() else discord.Colour.light_embed()
    embed.set_footer(text=f"invoked by {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
    return embed

def format_time(seconds):
    time_table = {
        "decade": seconds // 315576000,
        "year": seconds // 31557600 % 10,
        "day": seconds // 86400 % 365.25,
        "hour": seconds // 3600 % 24,
        "minute": seconds // 60 % 60,
        "second": seconds % 60,
    }
    
    return_string = ""
    
    for unit, value in time_table.items():
        value = math.floor(value)
        if value > 1:
            return_string += f"{value} {unit}s "
        elif value == 1:
            return_string += f"{value} {unit} "
    
    return return_string

async def can_run(ctx: commands.context, command: commands.command) -> bool:
    try:
        await command.can_run(ctx)
    except commands.CommandError:
        return False

    if command.hidden:
        return False
    
    return True