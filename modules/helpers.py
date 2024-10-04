
# helpers.py are discord bot specific, generic_helpers.py work in any python script

import discord
from discord.ext import commands

import os
import random
import math
import re

if __name__ == "__main__":
    import sys
    sys.path.append(".")

from objects import lang

# user still needs to set the title, description, and fields
def create_embed(ctx: commands.Context, user = None):
    if user == None:
        user = ctx.author
    
    embed = discord.Embed()
    embed.colour = user.colour if user.colour != discord.Colour.default() else discord.Colour.light_embed()
    embed.set_footer(
        text=lang.tr("default_embed_footer", userID=ctx.author.id, author=ctx.author.display_name),
        icon_url=ctx.author.display_avatar.url
    )
    return embed

async def can_run(ctx: commands.context, command: commands.command) -> bool:
    try:
        await command.can_run(ctx)
    except commands.CommandError:
        return False

    if command.hidden:
        return False
    
    return True