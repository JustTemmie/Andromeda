from datetime import datetime
from typing import Optional

from discord import Embed, Member, member
from discord.ext.commands import command, has_permissions, bot_has_permissions
from discord.ext.commands import Cog, Greedy
from discord.ext.commands import CheckFailure


class Admin(Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @command(name="kick")
    @bot_has_permissions(kick_members=True)
    @has_permissions(kick_members=True)
    async def kick_members(self, ctx, targets: Greedy[Member], *, reason:Optional[str] = "No reason provided"):
        if not len(targets):
            await ctx.send("One or more of the required arguments are missing")
            
        else:
            for target in targets:
                await target.kick(reason=reason)
                embed = Embed(title="Member kicked",
                              colour=0xDD2222,
                              timestamp=datetime.utcnow())

                fields = [("Member", f"{target.mention} a.k.a. {target.display_name}", False),
                          ("Actioned by", ctx.author.mention, False),
                          ("ID", target.id, False),
                          ("Name", str(target), False),
                          ("Created at in UTC", target.created_at.strftime("%d/%m/%Y %H:%M:%S"), True),
                          ("Joined at in UTC", target.joined_at.strftime("%d/%m/%Y %H:%M:%S"), True),
                          ("Top role", target.top_role.mention, False),
                          ("Reason", reason, False)]

                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)
                              
            embed.set_thumbnail(url=target.avatar_url)
            await self.bot.get_channel(772591539423281172).send(embed=embed)
            await ctx.send(embed=embed)
    
    @kick_members.error
    async def kick_members_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            await ctx.send("Insufficient permissions to perform tat task")
    
    @command(name="ban")
    @bot_has_permissions(ban_members=True)
    @has_permissions(ban_members=True)
    async def ban_members(self, ctx, targets: Greedy[Member], *, reason:Optional[str] = "No reason provided"):
        if not len(targets):
            await ctx.send("One or more of the required arguments are missing")

        else:
            for target in targets:
                await target.ban(reason=reason)
                    
                embed = Embed(title="Member banned",
                              colour=0xDD2222,
                              timestamp=datetime.utcnow())

                fields = [("Member", f"{target.mention} a.k.a. {target.display_name}", False),
                          ("Actioned by", ctx.author.mention, False),
                          ("ID", target.id, False),
                          ("Name", str(target), False),
                          ("Created at in UTC", target.created_at.strftime(
                              "%d/%m/%Y %H:%M:%S"), True),
                          ("Joined at in UTC", target.joined_at.strftime(
                              "%d/%m/%Y %H:%M:%S"), True),
                          ("Top role", target.top_role.mention, False),
                          ("Reason", reason, False)]

                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)
                    
            embed.set_thumbnail(url=target.avatar_url)
            await self.bot.get_channel(772591539423281172).send(embed=embed)
            await ctx.send(embed=embed)

    @ban_members.error
    async def ban_members_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            await ctx.send("Insufficient permissions to perform tat task")
    
    @Cog.listener()
    async def on_ready(self):
        await self.bot.stdout.send("Admin cog ready!")
        
        if not self.bot.ready:
            self.log_channel = self.bot.get_channel(772591539423281172)
            self.bot.cogs_ready.ready_up("admin")
            
            
def setup(bot):
    bot.add_cog(Admin(bot))