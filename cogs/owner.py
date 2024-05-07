import discord
from discord.ext import commands

import ast
import sys
import os
import re
import subprocess

import hatsune_miku.decorators as decorators


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


async def send_long_message(ctx, msg, preset_output=""):
    chunks = msg.splitlines()  # send this at the very top

    while chunks:
        output = ""
        while chunks and len(output) + len(chunks[0]) < 1994:
            output += chunks[0] + "\n"
            chunks.pop(0)

        await ctx.send(f"{preset_output}```{output}```")
        preset_output = ""


class Owner(commands.Cog):
    def __init__(self, miku):
        self.miku = miku

    @commands.is_owner()
    @commands.command(name="restart")
    async def restartCommand(self, ctx):
        print(dir(ctx))
        await ctx.send("Restarting the miku...")
        print("Terminated using `restart` command.")
        await self.miku.close()

    @decorators.is_host_owner()
    @commands.command(name="bash", aliases=["sh"])
    async def bashCommand(self, ctx, *, command):
        shell_output = subprocess.getoutput(command)

        await send_long_message(ctx, shell_output, f"`{command}` returned output:\n")

    @commands.is_owner()
    @commands.command(name="update", brief="Updates the bot by pulling from github")
    async def update_git_pull(self, ctx, restart="False"):
        try:
            subprocess.call(["git", "fetch"])
            git_commit = subprocess.check_output(["git", "log", "--name-status", "HEAD..origin"]).decode("utf-8")
            var = subprocess.check_output(["git", "pull"])
            output = var.decode("utf-8")
        except Exception as error:
            await ctx.send(f"```py\n{error}```")
            return
        
        pattern = r'(https?://\S+)'

        git_commit = re.sub(pattern, r'<\1>', git_commit)
        if git_commit == "":
            await ctx.send("up to date :3")
            return
        
        if len(git_commit) < 1975:
            await ctx.send(git_commit)
        
        else:
            git_commits = git_commit.split("commit ")
            for i in git_commits:
                await ctx.send(f"commit {i}")

        if len(output) < 1975:
            await ctx.send(f"```{output}```")

        else:
            n = 1994
            split_strings = []

            for index in range(0, len(output), n):
                split_strings.append(output[index : index + n])

            for message in split_strings:
                await ctx.send(f"```{message}```")

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
                await self.miku.close()
                

async def setup(miku):
    await miku.add_cog(Owner(miku))
