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
    embed.colour = user.colour
    embed.set_footer(text=f"invoked by {user.display_name}", icon_url=user.display_avatar.url)
    
    return embed

def format_time(seconds):
    time_table = {
        "days": seconds // 86400,
        "hours": (seconds // 3600) % 86400,
        "minutes": (seconds // 60) % 60,
        "seconds": seconds % 60,
    }
    
    return_string = ""
    
    for unit, value in time_table.items():
        if value > 0:
            return_string += f"{value} {unit} "
    
    return return_string