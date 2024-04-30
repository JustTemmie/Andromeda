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
def createEmbed(user):
    embed = discord.Embed()
    embed.colour = user.colour
    embed.set_footer(text=f"invoked by {user.display_name}", icon_url=user.display_avatar.url)
    
    return embed