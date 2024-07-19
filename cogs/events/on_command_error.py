import discord
from discord.ext import commands, tasks
from discord.errors import Forbidden
from discord.ext.commands import CommandNotFound, BadArgument, MissingRequiredArgument, CommandOnCooldown
from datetime import datetime

import logging
import json
import os

from time import time
from math import floor

IGNORE_EXCEPTIONS = (CommandNotFound)

class OnCommandError(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_command_error(self, ctx, exception):
        if isinstance(exception, CommandNotFound):
            pass

        elif isinstance(exception, MissingRequiredArgument):
            await self.bot.lang.tr_send(ctx, "error_command_event_missing_required_argument", prefix=ctx.prefix, command=ctx.command)

        elif isinstance(exception, commands.UserInputError):
            await self.bot.lang.tr_send(ctx, "error_command_event_user_input_error", exception=exception)
        
        elif isinstance(exception, CommandOnCooldown):
            await ctx.send(
                self.bot.lang.tr("error_command_event_on_cooldown", duration=round(exception.retry_after, 2)),
                delete_after=(exception.retry_after + 0.2),
            )

        elif isinstance(exception, Forbidden):
            await self.bot.lang.tr_send(ctx, "error_command_event_forbidden", exception=exception.text)
        
        elif isinstance(exception, commands.NotOwner):
            await ctx.send(exception)
        
        else:
            await self.bot.lang.tr_send(ctx, "error_command_event_unhandled", exception=exception)
            raise exception



async def setup(bot):
    await bot.add_cog(OnCommandError(bot))
