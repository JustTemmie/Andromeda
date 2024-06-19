import discord
from discord.ext import commands
from discord import app_commands

import json

import time

import re

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
    def __init__(self, miku):
        self.miku = miku

    @commands.command(
        name="remind",
        aliases=["remindme", "reminder"],
        brief='reminds you of something\nmiku remind god damn it tell her i like beavers in 1 d 2 h 30 m\nyou can use "days, hours, minutes, and seconds"',
    )
    async def reminder_command(self, ctx, *, reminder: str):
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

        send_time = round(time.time() + seconds, 3)
        if not self.save_reminder(reminder, send_time, ctx.author):
            return await ctx.send("an error has occured, exiting...")
        embed = self.create_embed(reminder, send_time, ctx.author)

        await ctx.send(embed=embed)


    @app_commands.command(
        name="remind",
        description="set a reminder!",
    )
    @app_commands.allowed_installs(guilds=True, users=True)
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

        send_time = round(time.time() + seconds, 3)
        if not self.save_reminder(reminder, send_time, intercation.user):
            return await intercation.response.send_message("an error has occured, exiting...")
        embed = self.create_embed(reminder, send_time, intercation.user)

        await intercation.response.send_message(embed=embed)


    def save_reminder(self, reminder, send_time, author) -> bool:
        with open("local_only/reminders.json", "r") as f:
            data = json.load(f)

        if not str(author.id) in data:
            data[str(author.id)] = {}

        data[str(author.id)][send_time] = reminder

        with open("local_only/reminders.json", "w") as f:
            json.dump(data, f)
        
        return True


    def create_embed(self, reminder, send_time, author) -> discord.Embed:
        embed = discord.Embed(title=reminder, description=f"i will remind you <t:{round(send_time)}:R>", color=author.colour)
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
