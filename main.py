import discord
from discord.ext import commands

from datetime import datetime
import json
import logging
import asyncio
import glob

import hatsune_miku.APIs.config as configLib 

miku = None

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        filename=f"logs/{datetime.now().strftime('%Y-%m-%d-%H:%M:%S')}.log",
        filemode="w",
        format="%(asctime)s:%(levelname)s:%(name)s:%(message)s",
    )

    logging.warning("warning")
    logging.error("error")
    logging.critical("critical")

    config = configLib.getConfig()


    def get_prefix(bot, message):
        return commands.when_mentioned_or(*config["PREFIXES"])(bot, message)


    class Miku(commands.AutoShardedBot):
        def __init__(self, *args, **kwargs):
            super().__init__(
                shards=config["SHARDS"],
                command_prefix=(get_prefix),
                strip_after_prefix=True,
                case_insensitive=True,
                owner_ids=config["OWNER_IDS"],
                intents=discord.Intents.all(),
            *args, **kwargs)

            self.start_time = datetime.now()
            self.custom_data = {
                "FFMPEG_PATH": "/usr/bin/ffmpeg",
                "SPOTIFY_PLAYLISTS": [
                    "https://open.spotify.com/playlist/37i9dQZF1DWZipvLjDtZYe",
                    "https://open.spotify.com/playlist/5lmxGE4yfbWGpXOtKL9eOB"
                    "https://open.spotify.com/album/0h6FjVSgPLOVJ37AduWrNZ?si=trT7KaH_Q3iFJ5qZyd893w",
                    "https://open.spotify.com/track/7aux5UvnlBDYlrlwoczifW?si=ce097ea45e604e04",
                ],
                "API_KEYS": config["API_KEYS"],
                "HOST_OWNERS": config["HOST_OWNERS"],
                "DEVELOPMENT": config["DEVELOPMENT"],
                "DOWNLOAD_ASSETS": config["DOWNLOAD_ASSETS"]
            }

        async def on_ready(self) -> None:
            print(f"Succesfully logged in as {self.user}")
        
        async def setup_hook(self) -> None:
            print(f"Syncing command tree...")
            if self.custom_data["DEVELOPMENT"]:
                guild = discord.Object(id=885113462378876948)
                self.tree.copy_global_to(guild=guild)
                await self.tree.sync()
            else:
                await self.tree.sync()
            print(f"Command tree synced!")
        

    miku = Miku()
    # miku.tree = discord.app_commands.CommandTree(miku)
    # miku.remove_command("help")

    @miku.tree.command(
        name="commandname",
        description="My first application Command",
        guild=discord.Object(id=885113462378876948)
    )
    async def first_command(interaction):
        await interaction.response.send_message("Hello!")
    
    
    async def main():
        async with miku:
            for filename in glob.iglob("./cogs/**", recursive=True):
                if filename.endswith(".py"):
                    # goes from "./cogs/economy.py" to "cogs.economy.py"
                    filename = filename[2:].replace("/", ".")[:-3]
                    # removes the ".py" from the end of the filename, to make it into cogs.economy
                    await miku.load_extension(filename)

            await miku.start(miku.custom_data["API_KEYS"]["DISCORD"])

    asyncio.run(main())


