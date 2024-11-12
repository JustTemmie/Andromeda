import discord
from discord.ext import commands

import modules.database.user as userDB

class BeforeInvoke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        @bot.before_invoke
        async def before_invoke(ctx):
            with userDB.Driver.SessionMaker() as db_session:
                user_query = db_session.query(userDB.User)
                user = user_query.where(userDB.User.id == ctx.author.id).first()
                
                if user:
                    return
            
            
            user = userDB.User()
            user.id = ctx.author.id
            
            with userDB.Driver.SessionMaker() as db_session:
                print(f"adding {ctx.author.display_name} to userDB")
                db_session.add(user)
                db_session.commit()
    
async def setup(bot):
    await bot.add_cog(BeforeInvoke(bot))
