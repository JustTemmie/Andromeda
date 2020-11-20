from random import choice, randint
from typing import Optional


from aiohttp import request
from discord import Member, Embed
from discord.errors import HTTPException
from discord.ext.commands import Cog
from discord.ext.commands import command, cooldown, BucketType
from discord.ext.commands import BadArgument

class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @command(name="some_command", aliases=["command", "c"]
             #, hidden=True hides from the default help command
             )
    @cooldown(1, 3, BucketType.user)
    async def semecommand(self, ctx):
        pass
    
    @command(name="hello", aliases=["hi", "hey"])
    @cooldown(1, 0.7, BucketType.guild)
    async def say_hello(self, ctx):
        await ctx.send(f"{choice(('Hello', 'Greetings', 'Bonjour', 'hi-ya','Sup', 'Privet', 'Привет', 'Hi', 'Good day', 'Howdy', 'Hey', 'Heyya'))} {ctx.author.mention}!")
        
    @command(name="dice", aliases=["roll"])
    @cooldown(1, 3, BucketType.user)
    async def roll_dice(self, ctx, die_string: str):
        dice, value = (int(value) for value in die_string.split("d"))
        
        if dice <= 25:
            rolls = [randint(1, value) for i in range(dice)]
            
            await ctx.send(" + ".join([str(r) for r in rolls]) + f" = {sum(rolls)}")
            
        else:
            await ctx.send("I can't roll that many dice. Please try a lower number")
    
#    @roll_dice.error
#    async def roll_dice_error(self, ctx, exc):
#        if isinstance(exc.original, HTTPException):
#            await ctx.send("The result was too large. Please try a lower number.")
# instead of using this we rather limited the number of dice as HTTPException is wack
            
    @command(name="slap", aliases=["hit"])
    @cooldown(2, 3, BucketType.user)
    async def slap_member(self, ctx, member: Member, *, reason: Optional[str] = "for no real reason"):
        await ctx.send(f"{ctx.author.display_name} slapped {member.mention} {reason}!")  

    @slap_member.error
    async def slap_member_error(self, ctx, exc):
        if isinstance(exc, BadArgument):
            await ctx.send("I can't find that member.")
            
    @command(name="echo", aliases=["please say", "repeat after me"])
    @cooldown(1, 3, BucketType.user)
    async def echo_message(self, ctx, *, message):
        await ctx.message.delete()
        await ctx.send(message)
        
    @command(name="fact", aliases=["info", "animal", "fun fact"], brief="brief description", description="The list of animals you can ask facts about are, dog, cat, panda, fox, birb, koala")
    @cooldown(1, 2.5, BucketType.guild)
    async def animal_fact(self, ctx, animal: str):
        if (animal := animal.lower()) in ("dog", "cat", "panda", "fox", "birb", "koala"):
            fact_url = f"https://some-random-api.ml/facts/{'bird' if animal == 'birb' else animal}"
            image_url = f"https://some-random-api.ml/img/{animal}"
            
            async with request("GET", image_url, headers={}) as response:
                if response.status == 200:
                    data = await response.json()
                    image_link = data["link"]
                    
                else:
                    image_link = None
            
            async with request("GET", fact_url, headers={}) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    embed = Embed(title=f"A random fact about {animal.title()}s",
                                  description=data["fact"],
                                  colour=ctx.author.colour)
                    if image_link is not None:
                        embed.set_image(url=image_link)
                    await ctx.send(embed=embed)
                
                else:
                    await ctx.send(f"API returned a {response.status} status.")
        
        else:
            await ctx.send("No facts are available for that animal, The list of animals you can ask facts about are dog, cat, panda, fox, birb, koala.")
    
    @Cog.listener()
    async def on_ready(self):
        await self.bot.stdout.send("Fun cog ready!")
        
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("fun")
        
    
def setup(bot):
    bot.add_cog(Fun(bot))
