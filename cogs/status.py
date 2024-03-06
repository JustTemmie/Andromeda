import discord
from discord.ext import commands, tasks

from mutagen.mp3 import MP3
import time
import asyncio
import logging

import hatsune_miku.helpers as helpers

class StatusChanger(commands.Cog):
    def __init__(self, miku):
        self.miku = miku
        self.changeStatusTask.start()
        self.song_name = "Miku"
        self.song_end_at = 0
    
        
    @tasks.loop(seconds=5)
    async def changeStatusTask(self):
        def getRandomSongData():
            song = helpers.getRandomSong()
            audio_data = MP3(song)
            if audio_data.info.length > 5:
                self.song_end_at = round(time.time() + audio_data.info.length)
                self.song_name = audio_data["TIT2"].text[0]
            else:
                getRandomSongData()
        
        if self.song_end_at < time.time():
            getRandomSongData()
            await self.miku.change_presence(
                status=discord.Status.idle,
                activity=discord.Activity(
                    type=discord.ActivityType.listening,
                    name=self.song_name),
            )

async def setup(miku):
    await miku.add_cog(StatusChanger(miku))
