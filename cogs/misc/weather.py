import discord
from discord.ext import commands
from discord import app_commands

import platform
import psutil
import subprocess
import time
from datetime import datetime
import requests
import json

from bs4 import BeautifulSoup
from pdf2image import convert_from_path


import hatsune_miku.helpers as helpers

class WeatherCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        @bot.tree.command(name="weather")
        @app_commands.allowed_installs(guilds=True, users=True)
        @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
        async def weather_command(interaction: discord.Interaction, location: str = bot.config["COMMAND_DEFAULTS"]["WEATHER_LOCATION"], ephemreal: bool = False) -> None:
            location = location.casefold()
            
            yrID = await self.get_yr_ID(location)
            
            if yrID == None:
                await interaction.response.send_message(f"sorry, i couldn't find a location named {location}", ephemeral=ephemreal)
                return
            
            image_path = await self.get_weather(yrID)
            
            av_button = discord.ui.Button(
                label="Open Externally",
                url=f"https://www.yr.no/en/print/forecast/{yrID}/",
                emoji="📩",
            )
            view = discord.ui.View()
            view.add_item(av_button)

            await interaction.response.send_message(file=discord.File(image_path), view=view, ephemeral=ephemreal)
            
    async def get_yr_ID(self, location) -> int:
        with open("local_only/yrCache.json", "r") as f:
            yr_cache = json.load(f)
        
        if location in yr_cache:
            if yr_cache[location]["timestamp"] + 5184000 > time.time():
                return yr_cache[location]["ID"]
        
        r = requests.get(f"https://www.yr.no/en/search?q={location}")
        
        soup = BeautifulSoup(r.content, "html.parser")
        
        results = soup.find_all("li")
        if len(results) == 0:
            return
        
        link = results[0].find("a", class_="search-results-list__item-anchor")
        link = link.get("href")
        ID = link.split("/")[4]
        
        yr_cache[location] = {
            "ID": ID,
            "timestamp": time.time()
        }
        
        with open("local_only/yrCache.json", "w") as f:
            json.dump(yr_cache, f)
        
        return ID

    async def get_weather(self, yrID):
        response = requests.get(f"https://www.yr.no/en/print/forecast/{yrID}/")

        with open(f"temp/yr-{yrID}.pdf", "wb") as f:
            f.write(response.content)

        convert_from_path(f"temp/yr-{yrID}.pdf", dpi=150)[0].save(f"temp/yr-{yrID}.png", "PNG")
        return f"temp/yr-{yrID}.png"



async def setup(bot):
    await bot.add_cog(WeatherCog(bot))
