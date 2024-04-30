import discord
from discord.ext import commands

import platform
import psutil
import subprocess
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

import hatsune_miku.helpers as helpers

class Info(commands.Cog):
    def __init__(self, miku):
        self.miku = miku
        self.start_time = time.time()

    async def get_info(self, page=1):
        uname = platform.uname()
        cpu_frequency = psutil.cpu_freq()
        
        if cpu_frequency != None:
            max_cpu_frequency = round(cpu_frequency.max / 1000, 2)
        else:
            max_cpu_frequency = "?"
        
        if page == 1:
            return {
                "System": f"{uname.system} {uname.release}",
                "Processor": f"{platform.machine()} CPU with {psutil.cpu_count()} threads, clocked at {max_cpu_frequency} GHz",
                "Memory": f"using {round(psutil.virtual_memory().used / 1024**2)}/{round(psutil.virtual_memory().total / 1024**2)} MB",
                "System Uptime": self.get_uptime(round(time.time() - psutil.boot_time())),
                "Bot Uptime": self.get_uptime(round(time.time() - self.start_time)),
                "Ping": f"{round(self.miku.latency * 1000)}ms",
                "Python": f"version {platform.python_version()}",
                "Discord.py": f"version {discord.__version__}"
            }
            
        else:
            return {}
            
    @commands.command(name="info")
    async def info_command(self, ctx):
        
        embed = helpers.createEmbed(ctx.author)
        embed.title = "Info"
        embed.description = "beavers?!"
        
        page_data = await self.get_info()
        for i in page_data:
            embed.add_field(
                name=i,
                value=page_data[i],
                inline=False
            )
        
        await ctx.send(embed=embed)

    
    def get_uptime(self, uptime):
        if uptime > 86400:
            fmt = '{0.days} days {0.hours} hours {0.minutes} minutes {0.seconds} seconds'
        else:
            fmt = '{0.hours} hours {0.minutes} minutes {0.seconds} seconds'
        
        return fmt.format(relativedelta(seconds=uptime))

async def setup(miku):
    await miku.add_cog(Info(miku))
