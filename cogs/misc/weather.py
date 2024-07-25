import discord
from discord.ext import commands
from discord import app_commands

import json
import time
import os
import requests
from bs4 import BeautifulSoup
from pdf2image import convert_from_path

import modules.helpers as helpers
import modules.localAPIs.database as DbLib
import modules.localAPIs.config as configLib
import modules.APIs.tenor as tenorLib

if __name__ == "__main__":
    import sys
    sys.path.append(".")

config = configLib.getConfig()
DEFAULT_WEATHER_LOCATION = config["COMMAND_DEFAULTS"]["WEATHER_LOCATION"]

class Weather(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="weather", aliases=["yr"],
        brief="get a weather forecast for the spcified location",
        extras={"page": "main", "category":"utility"}
    )
    async def weather_text_command(self, ctx: commands.Context, location: str = DEFAULT_WEATHER_LOCATION):
        yrID = self.get_yr_id(location.lower())
        if not yrID:
            await self.bot.lang.tr_send("weather_command_location_fetch_failed")
            return
        
        yr_embed_path = self.get_yr_embed(yrID)
        
        av_button = discord.ui.Button(
            label="Open Externally",
            url=f"https://www.yr.no/en/print/forecast/{yrID}/",
            emoji="📩",
        )
        view = discord.ui.View()
        view.add_item(av_button)

        await ctx.send(
            file=discord.File(yr_embed_path),
            view=view
        )
    
    @app_commands.command(
        name="weather",
        description="get a weather forecast for the spcified location"
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def weather_slash_command(
        self, intercation: discord.Interaction,
        location: str = DEFAULT_WEATHER_LOCATION
    ):
        yrID = self.get_yr_id(location.lower())
        if not yrID:
            await intercation.response.send_message(self.bot.lang.tr("weather_command_location_fetch_failed"))
            return

        yr_embed_path = self.get_yr_embed(yrID)
        
        av_button = discord.ui.Button(
            label="Open Externally",
            url=f"https://www.yr.no/en/print/forecast/{yrID}/",
            emoji="📩",
        )
        view = discord.ui.View()
        view.add_item(av_button)

        await intercation.response.send_message(
            file=discord.File(yr_embed_path),
            view=view
        )
    
    def get_yr_id(self, location: str) -> str | None:
        with open("local_only/yrIDs.json", "r") as f:
            yr_cache = json.load(f)
            
        if location in yr_cache:
            # check if the location was saved within the last month
            if yr_cache[location]["time"] + 2592000 > time.time():
                return yr_cache[location]["id"]
        
        r = requests.get(f"https://www.yr.no/en/search?q={location}")
        
        soup = BeautifulSoup(r.content, "html.parser")
        soup = soup.find("ol", class_="search-results-list")
        
        try:
            result = soup.find_all("li")[0]
        except:
            return None
        
        link = result.find("a", class_="search-results-list__item-anchor").get("href")
        ID = str(link.split("/")[4])
        
        yr_cache[location] = {
            "id": ID,
            "time": time.time()
        }
        
        with open("local_only/yrIDs.json", "w") as f:
            json.dump(yr_cache, f)
        
        return ID

    def get_yr_embed(self, yrID: int) -> str:
        if os.path.exists(f"temp/yr-{yrID}.png"):
            return f"temp/yr-{yrID}.png"
        
        r = requests.get(f"https://www.yr.no/en/print/forecast/{yrID}/")

        with open(f"temp/yr-{yrID}.pdf", "wb") as f:
            f.write(r.content)

        png = convert_from_path(f"temp/yr-{yrID}.pdf", dpi=150)[0]
        png.save(f"temp/yr-{yrID}.png", "PNG")

        return f"temp/yr-{yrID}.png"


async def setup(bot):
    await bot.add_cog(Weather(bot))
