import discord
from discord.ext import commands
from discord import app_commands

import typing
import copy
import os
from PIL import Image, ImageDraw, ImageFilter
from io import BytesIO

FLAG_DIR = "assets/images/flags"
PFP_SIZE = 1024

SEPARATORS = {
    "vertical |": ((PFP_SIZE / 2, 0), (PFP_SIZE, 0), (PFP_SIZE, PFP_SIZE), (PFP_SIZE / 2), PFP_SIZE),
    "horizontal -": ((0, PFP_SIZE / 2), (PFP_SIZE, PFP_SIZE / 2), (PFP_SIZE, PFP_SIZE), (0, PFP_SIZE)),
    "diagonal /": ((PFP_SIZE, 0), (PFP_SIZE, PFP_SIZE), (0, PFP_SIZE)),
    "diagonal \\": ((0, 0), (PFP_SIZE, 0), (PFP_SIZE, PFP_SIZE)),
}

FLAGS = []
FLAG_DISPLAY_NAMES = []
files = os.listdir(FLAG_DIR)
for file in sorted(files, key = lambda x: x):
    FLAGS.append(file)
    FLAG_DISPLAY_NAMES.append(os.path.splitext(os.path.basename(file))[0])


class PrideCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    async def seperator_autocomplete(self,
        interaction: discord.Interaction,
        current: str,
    ) -> typing.List[app_commands.Choice[str]]:
        seperators = []
        
        for seperator in SEPARATORS.keys():
            if current.lower() in seperator.lower():
                seperators.append(app_commands.Choice(name=seperator, value=seperator))
        
        return seperators

    async def flag_autocomplete(self,
        interaction: discord.Interaction,
        current: str,
    ) -> typing.List[app_commands.Choice[str]]:
        flags = []
        
        for flag, flag_file in zip(FLAG_DISPLAY_NAMES, FLAGS):
            if current.lower() in flag.lower():
                flags.append(app_commands.Choice(name=flag, value=flag_file))

        if len(flags) > 25:
            flags = flags[:24]
            flags.append(app_commands.Choice(
                name=self.bot.lang.tr("autocomplete_too_many_values", interaction=interaction),
                value="Pride.png"
            ))

        return flags
    
    @app_commands.command(name="flag", description="check what a flag looks like")
    @app_commands.autocomplete(flag=flag_autocomplete)
    async def flag_command(self, interaction: discord.Interaction, flag: str) -> None:
        await interaction.response.send_message(file=discord.File(f"{FLAG_DIR}/{flag}"))
    
    @app_commands.command(name="pride", description="get a pride-ified profile picture!")
    @app_commands.autocomplete(flag=flag_autocomplete, flag_2=flag_autocomplete, seperator=seperator_autocomplete)
    async def pride_command(self,
            interaction: discord.Interaction,
            flag: str,
            flag_2: typing.Optional[str],
            seperator: typing.Optional[str],
            user: typing.Optional[discord.Member],
            pfp_margin: int = 50,
            background_blur: int = 0,
            flag_overwrite: typing.Optional[discord.Attachment] = None,
            flag_2_overwrite: typing.Optional[discord.Attachment] = None,
    ) -> None:
        border_blur: int = 0
        
        flag = f"{FLAG_DIR}/{flag}"
        if flag_2:
            flag_2 = f"{FLAG_DIR}/{flag_2}"
        
        if flag_overwrite:
            flag = BytesIO(await flag_overwrite.read())
        
        if flag_2_overwrite:
            flag_2 = BytesIO(await flag_2_overwrite.read())
        
        if flag_2 and not seperator:
            seperator = "vertical |"
        
        if not user:
            user = interaction.user
        
        background_size = (PFP_SIZE, PFP_SIZE)
        background = self.init_image(flag, background_size)
        if flag_2:
            flag_2_image = self.init_image(flag_2, background_size)
            background = self.merge_images(background, flag_2_image, (PFP_SIZE, PFP_SIZE), seperator)
        
        if background_blur:
            background = background.filter(ImageFilter.GaussianBlur(background_blur))
        
        pfp = self.init_image(BytesIO(await user.display_avatar.read()), (PFP_SIZE - pfp_margin, PFP_SIZE - pfp_margin))
        
        image = self.render_circle_on_background(image=pfp, background=background, border_blur=border_blur)
        
        output = BytesIO()
        image.save(output, format="png")
        output.seek(0)
        
        await interaction.response.send_message(file=discord.File(output, filename="pride.png"))

    def merge_images(self, image_1: Image, image_2: Image, size: tuple, seperator: str) -> Image:
        mask_img = Image.new("L", size, color=0)
        mask_draw = ImageDraw.Draw(mask_img)

        mask_poly = SEPARATORS[seperator]
        mask_draw.polygon(mask_poly, fill=255)
        
        return Image.composite(image_2, image_1, mask_img)
        
    
    def render_circle_on_background(self, image: Image, background: Image, border_blur: int) -> Image:
        image_margin_x = background.size[0] - image.size[0]
        image_margin_y = background.size[1] - image.size[1]
        
        mask = Image.new("L", image.size, color=0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((image_margin_x, image_margin_y, image.size[0], image.size[1]), fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(border_blur))
        
        image = Image.composite(image, background, mask)
        
        return image
    
    def init_image(self, image, size: tuple) -> Image:
        image = Image.open(image)
        
        width, height = image.size
        if width != height:
            offset  = int(abs(height-width)/2)
            if width>height:
                image = image.crop([offset,0,width-offset,height])
            else:
                image = image.crop([0,offset,width,height-offset])
            
        image = image.resize(size)
        
        # prevent colour mode errors
        image = image.convert("RGBA")
        
        return image

async def setup(bot):
    await bot.add_cog(PrideCog(bot))

if __name__ == "__main__":
    import asyncio
    
    async def test():
        cog = PrideCog(None)
        
        pfp_margin = 40
        
        background = cog.init_image("assets/images/flags/Transfemme.png", (PFP_SIZE, PFP_SIZE))
        pfp = cog.init_image("assets/images/flags/Transgender.png", (PFP_SIZE, PFP_SIZE))
        
        image = cog.merge_images(background, pfp, (PFP_SIZE, PFP_SIZE), "diagonal /")
        
        image.save("local_only/image.png")
        pfp.save("local_only/pfp.png")
        background.save("local_only/background.png")
    
    asyncio.run(test())