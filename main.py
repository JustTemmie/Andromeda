import discord
from discord.ext import commands

import logging
import logging.handlers

from datetime import datetime
import time

import json
import asyncio
import glob
import os

import hatsune_miku.APIs.config as configLib 

miku = None

if __name__ == "__main__":
    config = configLib.getConfig()
    settings = configLib.getSettings()
    
    directories_to_make = ["local_only"]
    directories_to_empty = ["temp", "logs"]
    
    for dir in directories_to_make + directories_to_empty:
        if not os.path.exists(dir):
            os.mkdir(dir)
            
    if config["DEVELOPMENT"]:
        for dir in directories_to_empty:
            for file in os.listdir(dir):
                os.remove(f"{dir}/{file}")
    
    logger = logging.getLogger("discord")
    logger.setLevel(logging.INFO)
    logging.getLogger("discord.http").setLevel(logging.INFO)

    handler = logging.handlers.RotatingFileHandler(
        filename=f"logs/discord-{round(time.time())}.log",
        encoding="utf-8",
        maxBytes=128 * 1024 * 1024,  # 128 MiB
        backupCount=2,
    )
    dt_fmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter("[{asctime}] [{levelname:<8}] {name}: {message}", dt_fmt, style="{")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    class Miku(commands.AutoShardedBot):
        def __init__(self, *args, **kwargs):
            self.config = config
            self.settings = settings
            
            self.ready = False
            
            super().__init__(
                shards=self.config["SHARDS"],
                command_prefix=(self.get_prefix),
                strip_after_prefix=True,
                case_insensitive=True,
                owner_ids=self.config["OWNER_IDS"],
                intents=discord.Intents.all(),
            *args, **kwargs)

            self.start_time = datetime.now()

        async def get_prefix(self, message):
            return commands.when_mentioned_or(*self.config["PREFIXES"])(self, message)

        async def on_ready(self) -> None:
            print(f"Succesfully logged in as {self.user}")
            self.ready = True

        async def setup_hook(self) -> None:
            async def sync_tree(self):
                print(f"Syncing command tree...")
                if self.config["DEVELOPMENT"]:
                    guild = discord.Object(id=config["DEVELOPMENT_GUILD"])
                    self.tree.copy_global_to(guild=guild)
                    await self.tree.sync()
                else:
                    await self.tree.sync()
                print(f"Command tree synced!")
                
            if self.config["SYNC_TREE"]:
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
            
            await miku.start(miku.config["API_KEYS"]["DISCORD"])


    miku.loop = asyncio.new_event_loop()
    asyncio.set_event_loop(miku.loop)
    asyncio.run(main())
