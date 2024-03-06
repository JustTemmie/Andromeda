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