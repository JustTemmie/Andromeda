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

class Png2pdfCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        @bot.tree.command(name="pdf2png")
        @app_commands.allowed_installs(guilds=True, users=True)
        @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
        async def pdf2png_command_register(interaction: discord.Interaction, pdf: discord.Attachment, ephemreal: bool = True) -> None:
            await self.pdf2png_command(interaction, pdf, ephemreal)
            
    async def pdf2png_command(self, interaction: discord.Interaction, file: discord.Attachment, ephemreal: bool):
        if not file.filename.endswith("pdf"):
            interaction.response.send_message(f"{file.filename} doesn't seem to be a valid pdf file")
            return

        png_files = await self.pdf2png_converter(file)
        files = []
        for file in png_files:
            files.append(discord.File(file))

        await interaction.response.send_message(files=files, ephemeral=ephemreal)
    
    async def pdf2png_converter(self, file: discord.Attachment):
        response = requests.get(file.url)

        pdf_path = f"temp/pdf2png-{file.filename}"
        png_path = f"temp/pdf2png-{file.filename}".replace("pdf", "png")
        png_pathes = []
        
        with open(pdf_path, "wb") as f:
            f.write(response.content)

        pages = convert_from_path(pdf_path, dpi=400)
        for page_index in range(0, min(10, len(pages))):
            path = f"{page_index}-{png_path}"
            png_pathes.append(path)
            pages[page_index].save(path, "PNG")
        
        return png_pathes


async def setup(bot):
    await bot.add_cog(Png2pdfCog(bot))
