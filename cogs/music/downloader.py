from discord.ext import commands, tasks

import os
import subprocess
import threading
import logging

class Downloader(commands.Cog):
    def __init__(self, miku):
        self.miku = miku
        self.change_status_task.start()

    @tasks.loop(hours=27)
    async def change_status_task(self):
        def download_songs():
            # download assets from spotify
            logging.info("downloading music from Spotify")
            path = os.path.dirname(os.path.realpath(__name__))
            os.chdir("assets/music")
            for i in self.miku.custom_data["SPOTIFY_PLAYLISTS"]:
                logging.info(f"downloading {i}")
                subprocess.run(["../.././venv/bin/python", "-m", "spotdl", i], stdout=subprocess.DEVNULL)
            os.chdir(path)
            logging.info("finished downloading music from Spotify")

        # start downloading spotify songs on a different thread
        yt_dlp_thread = threading.Thread(target=download_songs)
        yt_dlp_thread.start()
    
async def setup(miku):
    await miku.add_cog(Downloader(miku))
