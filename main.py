import discord
from discord.ext import commands

from datetime import datetime
import json
import logging
import asyncio
import glob
import os

import hatsune_miku.APIs.config as configLib 

miku = None

if __name__ == "__main__":
    config = configLib.getConfig()
    
    directories = ["temp", "logs"]
    for dir in directories:
        if not os.path.exists(dir):
            os.mkdir(dir)
        if config["DEVELOPMENT"]:
            for file in os.listdir(dir):
                os.remove(f"{dir}/{file}")
    
    logging.basicConfig(
        level=logging.INFO,
        filename=f"logs/{datetime.now().strftime('%Y-%m-%d-%H:%M:%S')}.log",
        filemode="w",
        format="%(asctime)s:%(levelname)s:%(name)s:%(message)s",
    )

    logging.warning("warning")
    logging.error("error")
    logging.critical("critical")
    

    class Miku(commands.AutoShardedBot):
        def __init__(self, *args, **kwargs):
            self.config = config
            
            super().__init__(
                shards=self.config["SHARDS"],
                command_prefix=(self.get_prefix),
                strip_after_prefix=True,
                case_insensitive=True,
                owner_ids=self.config["OWNER_IDS"],
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
            }
            
            for i in self.config:
                self.custom_data[i] = self.config[i]
            
            self.start_time = datetime.now()

        async def get_prefix(self, message):
            return commands.when_mentioned_or(*self.config["PREFIXES"])(self, message)

        async def on_ready(self) -> None:
            print(f"Succesfully logged in as {self.user}")

        async def setup_hook(self) -> None:
            async def sync_tree(self):
                print(f"Syncing command tree...")
                if self.custom_data["DEVELOPMENT"]:
                    guild = discord.Object(id=config["DEVELOPMENT_GUILD"])
                    self.tree.copy_global_to(guild=guild)
                    await self.tree.sync()
                else:
                    await self.tree.sync()
                print(f"Command tree synced!")
                
            if self.custom_data["SYNC_TREE"]:
                await sync_tree(self)
            else:
                print("miku is set to not sync tree, continuing")
        

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

    miku.loop = asyncio.new_event_loop()
    asyncio.set_event_loop(miku.loop)
    asyncio.run(main())


 