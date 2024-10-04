import discord
from discord.ext import commands
from discord import app_commands

import json
import time

import re

import modules.localAPIs.database as DbLib

# crazy ass regex that accepts strings such as "2 d", "5 days", "8day", "2.8hrs" and so on
time_patterns = {
    "days": r"(\d+(?:\.\d+)?)\s*d\w*",
    "hours": r"(\d+(?:\.\d+)?)\s*h\w*",
    "minutes": r"(\d+(?:\.\d+)?)\s*m\w*",
    "seconds": r"(\d+(?:\.\d+)?)\s*s\w*"
}

time_factors = {
    "days": 86400,
    "hours": 3600,
    "minutes": 60,
    "seconds": 1
}


class reminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="remind",
        aliases=["remindme", "reminder"],
        brief="command_brief_remind",
        usage=f'<reminder> in <duration>\nyou can use "days, hours, minutes, and seconds"',
        extras={"page": "main", "category":"utility"}
    )
    async def remind_command(self, ctx, *, reminder: str):
        if " in " not in reminder:
            await ctx.send('could not find the seperator "in" within the reminder, please try again')
            return
        
        time_string = reminder.rsplit(" in ", 1)
        seconds = self.string_to_seconds(time_string[1])
        reminder = time_string[0]
        
        if seconds < 20:
            return await ctx.send(f"please set a time greater than 20 seconds")

        if seconds > 94694400:
            return await ctx.send(f"please set a time less than 3 years")

        send_time = round(time.time() + seconds)
        if not self.save_reminder(ctx.message.id, send_time, ctx.author, reminder):
            return await ctx.send("an error has occured, exiting...")
        embed = self.create_embed(reminder, send_time, ctx.author)

        await ctx.send(embed=embed)


    @app_commands.command(
        name="remind",
        description="set a reminder!",
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.describe(reminder="The thing you want to be reminded about")
    async def reminder_slash_command(
                self, intercation: discord.Interaction, reminder: str,
                days: float = 0.0, hours: float = 0.0,
                minutes: float = 0.0, seconds: float = 0.0
    ):
        seconds = (
                time_factors["days"] * days
                + time_factors["hours"] * hours
                + time_factors["minutes"] * minutes
                + time_factors["seconds"] * seconds
        )
        
        if seconds < 20:
            return await intercation.response.send_message(f"please set a time greater than 20 seconds")

        if seconds > 94694400:
            return await intercation.response.send_message(f"please set a time less than 3 years")

        send_time = round(time.time() + seconds)
        if not self.save_reminder(intercation.id, send_time, intercation.user, reminder):
            return await intercation.response.send_message("an error has occured, exiting...")
        embed = self.create_embed(reminder, send_time, intercation.user)

        await intercation.response.send_message(embed=embed)


    def save_reminder(self, entry_ID, send_time, author, reminder_content) -> bool:
        DbLib.reminder_table.write(
            entry_ID,
            send_time,
            author.id,
            reminder_content
        )
        
        return True


    def create_embed(self, reminder, send_time, author) -> discord.Embed:
        embed = discord.Embed(title=reminder, description=f"i will remind you <t:{round(send_time + 5)}:R>", color=author.colour)
        embed.set_footer(text=f"{author.name}", icon_url=author.display_avatar.url)

        return embed


    def string_to_seconds(self, time_string):
        total_seconds = 0
        
        for unit, pattern in time_patterns.items():
            matches = re.findall(pattern, time_string, re.IGNORECASE)
            for match in matches:
                value = float(match)
                total_seconds += value * time_factors[unit]
        
        return total_seconds


async def setup(bot):
    await bot.add_cog(reminder(bot))
