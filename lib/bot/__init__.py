from asyncio import sleep
from datetime import datetime
from glob import glob

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord import Intents
from discord import Embed, File
from discord.errors import HTTPException, Forbidden
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import Context
from discord.ext.commands import (CommandNotFound, BadArgument, MissingRequiredArgument,
                                  CommandOnCooldown)
from discord.ext.commands import when_mentioned_or

from ..db import db

PREFIX = "+"
OWNER_IDS = [368423564229083137]
COGS = [path.split("\\")[-1][:-3] for path in glob("./lib/cogs/*.py")]
IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument)


def get_prefix(bot, message):
    return when_mentioned_or(PREFIX)(bot, message)


class Ready(object):
    def __init__(self):
        for cog in COGS:
            setattr(self, cog, False)
            
    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f" {cog} cog ready")
        
    def all_ready(self):
        return all([getattr(self,cog) for cog in COGS])
        
        
class Bot(BotBase):
    def __init__(self):
        self.PREFIX = PREFIX
        self.ready = False
        self.cog_ready = Ready()
                
        self.guild = None
        #wouldn't need it for a multi server bot
        self.scheduler = AsyncIOScheduler()
        
        db.autosave(self.scheduler)                
        super().__init__(
            command_prefix=get_prefix,
            owner_ids=OWNER_IDS,
            intents=Intents.all(),
        )
        
    def setup(self):
        for cog in COGS:
            self.load_extension(f"lib.cogs.{cog}")
            print(f"{cog} cog loaded")
            
        print(" setup complete")
            
    def run(self, version):
        self.VERSION = version
        
        print(" running setup...")
        self.setup()
        
        with open("./lib/bot/token.0", "r", encoding="utf-8") as tf:
            self.TOKEN = tf.read()
    
        print("running bot...")
        super().run(self.TOKEN, reconnect=True)
        
    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=Context)
        
        if ctx.command is not None and ctx.guild is not None:
            if self.ready:
                await self.invoke(ctx) 
            else:
                await ctx.send("I'm not ready to recieve commands yet. Please wait a few seconds.")
            
    async def Rules_reminder(self):
        await self.stdout.send("remember to follow the rules UwU")       
        
        
    async def on_connect(self):
        print(" Connected!")

    async def on_disconnect(self):
        print("bot disconnected")
        
    async def on_error(self, err, *args, **kwargs):
        if err == "on_command_error":
            await args[0].send("Sorry, something unexpected went wrong.")
            
            #await self.stdout.send("an error occured")   
            #raise
    
    async def on_command_error(self, ctx, exc):
        if any([isinstance(exc, error) for error in IGNORE_EXCEPTIONS]):
            #await ctx.send("Sorry, I couldn't find the command")
            pass
        
        elif isinstance(exc, MissingRequiredArgument):
            await ctx.send("One or more required arguments are missing.")
        
        elif isinstance(exc, CommandOnCooldown):
            await ctx.send(f"That command is on {str(exc.cooldown.type).split('.')[-1]} cooldown. Please try again in {exc.retry_after:,.2f} seconds.")
        
#        elif isinstance(exc.original, HTTPException):
#            await ctx.send("Unable to send message.")
            
        elif hasattr(exc, "original"):
            #raise exc  # .original
        
            if isinstance(exc.original, Forbidden):
                await ctx.send("I do not have the permission to do that.")
            
            else:
                raise exc.original
            
        else:
            raise exc
            
    async def on_ready(self):
        if not self.ready:
            self.ready = True
            self.guild = self.get_guild(628212961218920477)
            self.stdout = self.get_channel(767861117216227338)
            await self.stdout.send("Andromeda is ready!")
            self.scheduler.start()
            self.scheduler.add_job(self.print_message, CronTrigger(day_of_week=0, hour=12, minute=0, second=0))
            
            #while not self.cogs_ready.all_ready():
            #    await sleep(0.5)
            print(" bot ready")
            
            
#            embed = Embed(title="Now online", description="epic description",
#                          colour=0xFF0000, timestamp=datetime.utcnow())
#            fields = [("Name", "Value", True),
#                      ("Another field", "This field is next to theother one.", True),
#                      ("a non inline field", "this field will appear on it's own row", False)]
#            for name, value, inline in fields:
#                embed.add_field(name=name, value=value, inline=inline)
#            embed.set_author(name="temmite temite tmeitmeite", icon_url=self.guild.icon_url)
#            embed.set_footer(text="this is the fuckin footer")
#            embed.set_thumbnail(url=self.guild.icon_url)
#            embed.set_image(url=self.guild.icon_url)
#            await channel.send(embed=embed)
#            
#            await channel.send(file=File("./data/images/1200px-Andromeda_Galaxy_(with_h-alpha).jpg"))

        else:
            print("bot reconnected")

    async def on_message(self, message):
        #if message.author.bot and message.author != message.guild.me:
        #    pass
        if not message.author.bot:
            await self.process_commands(message)

    

bot = Bot()
