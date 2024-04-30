import discord

import os
import random

def getRandomSong():
    folder = "assets/music"
    files = os.listdir(folder)
    song = random.choice(files)
    return f"{folder}/{song}"

def getProgressBar(current, max, width = 20):
    percent = int(width * current / max)
    bar = "█" * percent + "░" * (width - percent)

    return bar

# user still needs to set the title, description, and fields
def create_embed(user):
    embed = discord.Embed()
    # set the colour to the user colour, unless it's black, in that case default to white (#ffffff)
    embed.colour = user.colour if user.colour != discord.Colour(000000) else discord.Colour(16777215)
    embed.set_footer(text=f"invoked by {user.display_name}", icon_url=user.display_avatar.url)
    
    return embed

def format_time(seconds):
    time_table = {
        "year": (seconds // 31557600) % 31557600,
        "day": (seconds // 86400) % 86400,
        "hour": (seconds // 3600) % 3600,
        "minute": (seconds // 60) % 60,
        "second": seconds % 60,
    }
    
    return_string = ""
    
    for unit, value in time_table.items():
        if value > 1:
            return_string += f"{value} {unit}s "
        elif value == 1:
            return_string += f"{value} {unit} "
    
    return return_string