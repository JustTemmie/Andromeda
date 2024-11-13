import discord
from discord.ext import commands
from discord import app_commands

import json
import time
import os
from math import floor
import requests
from bs4 import BeautifulSoup
from pdf2image import convert_from_path

if __name__ == "__main__":
    import sys
    sys.path.append(".")
    

from objects import lang
import config

DEFAULT_WEATHER_LOCATION = config.COMMAND_DEFAULTS["WEATHER_LOCATION"]

class Weather(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="weather", aliases=["yr"],
        brief="command_brief_weather",
        extras={"page": "main", "category":"utility"}
    )
    async def weather_text_command(self, ctx: commands.Context, location: str = DEFAULT_WEATHER_LOCATION):
        yrID = self.get_yr_id(location.lower())
        if not yrID:
            await lang.tr_send(ctx, "weather_command_location_fetch_failed")
            return
        
        yr_embed_path = self.get_yr_embed(
            yrID,
            language=lang.get_user_language(userID=ctx.author.id),
            forecast_link="https://" + lang.tr("weather_command_yr_link", userID=ctx.author.id, yrID=yrID)
        )
        
        av_button = discord.ui.Button(
            label=lang.tr("weather_command_open_link_externally", userID=ctx.author.id),
            url="https://" + lang.tr("weather_command_yr_link", userID=ctx.author.id, yrID=yrID),
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
        description="get a weather forecast for the specified location"
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.describe(location="Name of the region you want to query the weather for")
    async def weather_slash_command(
        self, interaction: discord.Interaction,
        location: str = DEFAULT_WEATHER_LOCATION
    ):
        await interaction.response.defer()
        yrID = self.get_yr_id(location.lower())
        if not yrID:
            original_response = await interaction.original_response()
            await original_response.edit(content=lang.tr("weather_command_location_fetch_failed", interaction=interaction))
            return

        yr_embed_path = self.get_yr_embed(
            yrID,
            language=lang.get_user_language(interaction=interaction),
            forecast_link="https://" + lang.tr("weather_command_yr_link", interaction=interaction, yrID=yrID)
        )
        
        av_button = discord.ui.Button(
            label=lang.tr("weather_command_open_link_externally", interaction=interaction),
            url="https://" + lang.tr("weather_command_yr_link", interaction=interaction, yrID=yrID),
            emoji="📩",
        )
        view = discord.ui.View()
        view.add_item(av_button)
        
        original_response = await interaction.original_response()
        await original_response.edit(
            attachments=[discord.File(yr_embed_path)],
            view=view
        )
    
    
    def get_yr_id(self, location: str) -> str:
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

    def get_yr_embed(self, yrID: str, language: str, forecast_link: str) -> str:
        unix_hour = floor(time.time() / 3600)
        
        png_path = f"temp/yr-{unix_hour}-{language}-{yrID}.png"
        pdf_path = f"temp/yr-{unix_hour}-{language}-{yrID}.pdf"
        
        if os.path.exists(png_path):
            return png_path
        
        r = requests.get(forecast_link)

        with open(pdf_path, "wb") as f:
            f.write(r.content)

        png = convert_from_path(pdf_path, dpi=200)[0]
        png.save(png_path, "PNG")

        return png_path


async def setup(bot):
    await bot.add_cog(Weather(bot))
