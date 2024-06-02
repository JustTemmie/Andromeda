
import discord
from discord.ext import commands
from discord import app_commands

from PIL import Image, ImageEnhance, ImageFilter
from io import BytesIO

class DeepFryCog(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        
        @bot.tree.context_menu(name="Deep Fry")
        async def deep_fry_context_command(interaction: discord.Interaction, message: discord.Message) -> None:
            if len(message.attachments) == 0:
                await interaction.response.send_message("that message doesn't seem to have any attachments", ephemeral=True)
                return
            
            files = []
            
            for attachment in message.attachments:
                image = BytesIO(await attachment.read())
                
                image = Image.open(image)
                
                if not image.verify():
                    continue
                
                image = image.convert("RGBA")
                
                for i in range(2):
                    image = image.filter(ImageFilter.SHARPEN)
                
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(5)
                
                image = ImageEnhance.Brightness(image).enhance(0.5)

                enhancer = ImageEnhance.Color(image)
                image = enhancer.enhance(5)
                
                for i in range(2):
                    image = image.filter(ImageFilter.SHARPEN)

                image = ImageEnhance.Brightness(image).enhance(2)
                
                files.append(image)
            
            await interaction.response.send_message(files=files)


async def setup(bot):
    await bot.add_cog(DeepFryCog(bot))