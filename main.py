import discord
from discord.ext import commands

import logging
import logging.handlers

from datetime import datetime
import asyncio
import glob
import os

import config

# create some folders what are required for a first run
directories_to_make = [
    "local_only",
    "local_only/databases",
    "assets",
    "assets/music",
    "assets/audio",
    "assets/videos",
    "assets/images",
    "assets/misc",
    "assets/language_data",
]

directories_to_empty = ["temp", "logs"]

files_to_make = {
    "local_only/yrIDs.json": "{}"
}

for path in directories_to_make + directories_to_empty:
    if not os.path.exists(path):
        print(f'creating folders at: "{path}"')
        os.mkdir(path)

for path, content in files_to_make.items():
    if not os.path.exists(path):
        print(f'creating file at: "{path}" with content: "{content}"')
        with open(path, "w") as f:
            f.write(content)
    
        
if config.DEVELOPMENT:
    for dir in directories_to_empty:
        for file in os.listdir(dir):
            os.remove(f"{dir}/{file}")

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
logging.getLogger('discord.http').setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(
    filename='logs/discord.log',
    encoding='utf-8',
    maxBytes=32 * 1024 * 1024,  # 32 MiB
)
dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)


class Bot(commands.AutoShardedBot):
    def __init__(self, *args, **kwargs):        
        self.ready = False
        
        super().__init__(
            shards=config.SHARDS,
            command_prefix=(self.get_prefix),
            strip_after_prefix=True,
            case_insensitive=True,
            owner_ids=config.OWNER_IDS,
            intents=discord.Intents.all(),
        *args, **kwargs)

        self.start_time = datetime.now()

    async def get_prefix(self, message):
        return commands.when_mentioned_or(*config.PREFIXES)(self, message)

    async def on_ready(self) -> None:
        print(f"Succesfully logged in as {self.user}")
        self.ready = True

    async def setup_hook(self) -> None:
        async def sync_tree(self):
            print(f"Syncing command tree...")
            if config.DEVELOPMENT:
                guild = discord.Object(id=config.DEVELOPMENT_GUILD)
                # self.tree.clear_commands(guild=guild)
                await self.tree.sync(guild=guild)
            else:
                await self.tree.sync()
            print(f"Command tree synced!")
            
        if config.SYNC_TREE:
            await sync_tree(self)
        else:
            print(f"bot is set to not sync tree, continuing")
    

bot = Bot()
if not bot.tree:
    bot.tree = discord.app_commands.CommandTree(bot)

@bot.tree.command(
    name="nickname",
    description="heh, hi :3",
    guild=discord.Object(id=885113462378876948)
)
async def nickname_command(interaction, victim: discord.Member, new_name: str):
    original_name = victim.display_name
    await victim.edit(nick=new_name)
    await interaction.response.send_message(f"renamed {original_name} to {new_name}", ephemeral=True)
    

async def init():
    async with bot:
        
        if len(config.COG_LIST_OVERWRITES) >= 1:
            for cog in config.COG_LIST_OVERWRITES:
                await bot.load_extension(f"cogs.{cog}")
        
        else:
            for filename in glob.iglob("./cogs/**", recursive=True):
                if filename.endswith(".py"):
                    # goes from "./cogs/economy.py" to "cogs.economy"
                    filename = filename[2:].replace("/", ".")[:-3]
                    await bot.load_extension(filename)
        
        await bot.start(config.API_KEYS["DISCORD"])

bot.loop = asyncio.new_event_loop()
asyncio.set_event_loop(bot.loop)
asyncio.run(init())
