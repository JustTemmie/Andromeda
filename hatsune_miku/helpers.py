import os
import random

def get_random_song():
    folder = "assets/music"
    files = os.listdir(folder)
    song = random.choice(files)
    return f"{folder}/{song}"