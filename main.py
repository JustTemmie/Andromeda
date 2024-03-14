import discord
from discord.ext import commands

from datetime import datetime
import json
import logging
import asyncio
import glob

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

    with open("config.json", "r") as f:
        config = json.load(f)


    def get_prefix(bot, message):
        return commands.when_mentioned_or(*config["PREFIXES"])(bot, message)


    class Miku(commands.AutoShardedBot):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.start_time = datetime.now()

        async def on_ready(self):
            
            print(f"Succesfully logged in as {self.user}")


    miku = Miku(
        shards=config["SHARDS"],
        command_prefix=(get_prefix),
        strip_after_prefix=True,
        case_insensitive=True,
        owner_ids=config["OWNER_IDS"],
        intents=discord.Intents.all(),
    )

    miku.custom_data = {
        "HOST_OWNERS": config["HOST_OWNERS"],
        "FFMPEG_PATH": "/usr/bin/ffmpeg",
        "SPOTIFY_PLAYLISTS": [
            "https://open.spotify.com/playlist/37i9dQZF1DWZipvLjDtZYe",
            "https://open.spotify.com/playlist/5lmxGE4yfbWGpXOtKL9eOB"
            "https://open.spotify.com/album/0h6FjVSgPLOVJ37AduWrNZ?si=trT7KaH_Q3iFJ5qZyd893w",
            "https://open.spotify.com/track/7aux5UvnlBDYlrlwoczifW?si=ce097ea45e604e04",
        ],
        "DOWNLOAD_ASSETS": config["DOWNLOAD_ASSETS"]
    }

    # miku.tree = discord.app_commands.CommandTree(miku)
    # miku.remove_command("help")

    @miku.tree.command(
        name="commandname",
        description="My first application Command",
        guild=discord.Object(id=903236631958548501)
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

            await miku.start(config["TOKEN"])

    asyncio.run(main())
