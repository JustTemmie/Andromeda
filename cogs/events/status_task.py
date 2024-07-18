import discord
from discord.ext import commands, tasks

import random
import time

import modules.helpers as helpers

class StatusChanger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.change_status_task.start()
    
    
    @commands.Cog.listener()
    async def on_ready(self):
        for i in self.bot.settings["STATUSES"]:
            await self.parse_status(i)
    
    
    async def parse_status(self, status):
        try:
            status = eval(f' f"{status}" ')
            if len(status) > 128:
                print(f"error, status message was over 128 characters:\n {status}")
                status = "whoopsie, my status was too long"
        except Exception as e:
            print(f"error while setting status :( - {e}" )
        
        activity_enum = {
            "unknown": -1, # don't use this one :3
            "playing": 0,
            "streaming": 1,
            "listening": 2,
            "watching": 3,
            "custom": 4, # or this one
            "competing": 5,
        }
        
        activity_mode = 0
        
        for key, value in activity_enum.items():
            if status.startswith(f"{key}-"):
                activity_mode = value
                status = status.replace(f"{key}-", "")
                break
        
        return (status, activity_mode)
    
    
    @tasks.loop(minutes=30)
    async def change_status_task(self):
        await self.bot.wait_until_ready()
        status = random.choice(self.bot.settings["STATUSES"])
        
        status, activity_mode = await self.parse_status(status)
        
        await self.bot.change_presence(
            status=discord.Status.online,
            activity=discord.Activity(
                type=discord.ActivityType(activity_mode),
                name=status
            ),
        )

async def setup(bot):
    await bot.add_cog(StatusChanger(bot))
