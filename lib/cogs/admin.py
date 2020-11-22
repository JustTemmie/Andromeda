from asyncio import sleep
from datetime import datetime, timedelta
from re import search
from typing import Optional

from discord import Embed, Member, NotFound, Object
from discord.utils import find
from discord.ext.commands import Cog, Greedy, Converter
from discord.ext.commands import CheckFailure, BadArgument
from discord.ext.commands import command, has_permissions, bot_has_permissions


class Admin(Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @command(name="kick", brief="Kicks the specified user")
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
    
    @command(name="ban", brief="Bans the specified user")
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
    
    @command(name="clear", aliases=["purge"], brief="Clears sum messages")
    @bot_has_permissions(manage_messages=True)
    @has_permissions(manage_messages=True)
    async def clear_messages(self, ctx, targets: Greedy[Member], limit: Optional[int] = 5):
        def _check(message):
            return not len(targets) or message.author in targets
        
        if 0 < limit <= 100:
            with ctx.channel.typing():
                await ctx.message.delete()
                deleted = await ctx.channel.purge(limit=limit, after=datetime.utcnow()-timedelta(days=14),
												                                check=_check)
                
                await ctx.send(f"Deleted {len(deleted):,} messages.", delete_after=7.5)
    
        else:
            await ctx.send("The limit provided is not within acceptable bounds.")
    
    
    @Cog.listener()
    async def on_ready(self):
        await self.bot.stdout.send("Admin cog ready!")
        
        if not self.bot.ready:
            self.log_channel = self.bot.get_channel(772591539423281172)
            self.bot.cogs_ready.ready_up("admin")
            
            
def setup(bot):
    bot.add_cog(Admin(bot))
