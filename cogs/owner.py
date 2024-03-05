import discord
from discord.ext import commands
from discord.ext.commands import bot_has_permissions

import ast
import sys
import os
import asyncio



import subprocess
import datetime
import re
import json
import time
import random
import contextlib
import io


def insert_returns(body):
    # insert return stmt if the last expression is a expression statement
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    # for if statements, we insert returns into the body and the or else
    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    # for with blocks, again we insert returns into the body
    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)


class Owner(commands.Cog):
    def __init__(self, miku):
        self.miku = miku

    @commands.is_owner()
    @commands.command(name="restart", aliases=["reboot"])
    async def restart(self, ctx):
        await self.miku.change_presence(
            status=discord.Status.idle,
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="Restarting - won't respond!",
            ),
        )
        await ctx.send("Restarting miku...")
        python = sys.executable
        os.execl(python, python, *sys.argv)

    @commands.is_owner()
    @commands.command(name="shutdown")
    async def shutdown(self, ctx):
        await ctx.send("Turning off the miku...")
        await self.miku.change_presence(
            status=discord.Status.idle,
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="About to go offline - won't respond!",
            ),
        )
        await self.miku.close()
        print("Terminated using `shutdown` command.")

    @commands.is_owner()
    @commands.command(name="bash", aliases=["sh"])
    async def run_bash(self, ctx, *, command):
        shell_output = subprocess.getoutput(command)
        
        output = f"`{command}` returned output:\n"
        chunks = shell_output.splitlines()

        while chunks:
            while chunks and len(output) + len(chunks[0]) < 1994:
                output += chunks[0] + "\n"
                chunks.pop(0)
            
            await ctx.send(f"```{output}```")
            output = ""
    
    @commands.command(name="update", brief="Updates the bot by pulling from github")
    @commands.is_owner()
    async def update_git_pull(self, ctx, restart="False"):
        try:
            subprocess.call(["git", "fetch"])
            git_commit = subprocess.check_output(["git", "log", "--name-status", "HEAD..origin"]).decode("utf-8")
            var = subprocess.check_output(["git", "pull"])
            shell_output = f"{git_commit}\n\n{var.decode('utf-8')}"
        except Exception as error:
            await ctx.send(f"```py\n{error}```")
            return

        chunks = shell_output.splitlines()

        while chunks:
            output = ""
            while chunks and len(output) + len(chunks[0]) < 1994:
                output += chunks[0] + "\n"
                chunks.pop(0)
            
            await ctx.send(f"```{output}```")

        if var.decode("utf-8") != "Already up to date.\n":
            if restart.lower() == "true":
                await ctx.send("Restarting...")
                await self.bot.change_presence(
                    status=discord.Status.idle,
                    activity=discord.Activity(
                        type=discord.ActivityType.watching,
                        name="restarting - won't respond",
                    ),
                )
                os.execv(sys.executable, ["python3"] + sys.argv)
                return
        
async def setup(miku):
    await miku.add_cog(Owner(miku))
