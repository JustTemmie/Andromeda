from discord.ext import commands, tasks

import os
import random
import logging
import asyncio

class Downloader(commands.Cog):
    def __init__(self, miku):
        self.miku = miku
        self.downloadSpotifyLists.start()
    
        
    @tasks.loop(hours=27)
    async def downloadSpotifyLists(self):
        # download assets from spotify
        logging.info("downloading music from Spotify")
        path = os.path.dirname(os.path.realpath(__name__))
        os.chdir("assets/music")
        for i in self.miku.custom_data["SPOTIFY_PLAYLISTS"]:
            logging.info(f"downloading {i}")

            process = await asyncio.create_subprocess_exec(
                "screen", "-dmS", f"spotdl-{random.randint(0, 9999999)}", "../.././venv/bin/python", "-m", "spotdl", f"{i}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            # wait for the subprocess to finish
            stdout, stderr = await process.communicate()

            # handle stdout and stderr if needed
            if stdout:
                print(f'STDOUT: {stdout.decode()}')
                logging.info(f'STDOUT: {stdout.decode()}')
            if stderr:
                print(f'STDERR: {stderr.decode()}')
                logging.info(f'STDERR: {stderr.decode()}')
            
        os.chdir(path)
        logging.info("finished downloading music from Spotify")
    
async def setup(miku):
    await miku.add_cog(Downloader(miku))
