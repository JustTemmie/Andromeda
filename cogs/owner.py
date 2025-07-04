import discord
from discord.ext import commands

import ast
import sys
import os
import re
import subprocess

import modules.decorators as decorators


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
    def __init__(self, bot):
        self.bot = bot

    @commands.is_owner()
    @commands.command(
        name="shutdown",
        extras={"page": "admin", "category":"owner"}
    )
    async def shutdown_command(self, ctx):
        await ctx.send("shutting down...")
        print("Terminated using `shutdown` command.")
        await self.bot.close()

    @decorators.is_host_owner()
    @commands.command(
        name="bash", aliases=["sh"],
        extras={"page": "admin", "category":"owner"}
    )
    async def bashCommand(self, ctx, *, command):
        shell_output = subprocess.getoutput(command)

        await send_long_message(ctx, shell_output, f"`{command}` returned output:\n")

    @commands.is_owner()
    @commands.command(
        name="update", brief="command_brief_update",
        extras={"page": "admin", "category":"owner"}
    )
    async def update_git_pull(self, ctx, restart="False"):
        try:
            subprocess.call(["git", "fetch"])
            git_commit = subprocess.check_output(["git", "log", "--name-status", "HEAD..origin"]).decode("utf-8")
            var = subprocess.check_output(["git", "pull"])
            output = var.decode("utf-8")
        except Exception as error:
            await ctx.send(f"```\n{error}```")
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
            if restart.lower() in ["true", "1"]:
                await ctx.send("Restarting...")
                await self.bot.change_presence(
                    status=discord.Status.idle,
                    activity=discord.Activity(
                        type=discord.ActivityType.watching,
                        name="restarting - won't respond",
                    ),
                )
                await self.bot.close()
    
    # command to run python stuff
    @commands.is_owner()
    @commands.command(
        name="run", brief="command_brief_run",
        extras={"page": "admin", "category":"owner"}
    )
    async def run_command(self, ctx, *, code: str):
        fn_name = "_eval_expr"

        code = code.strip("` ")  # get rid of whitespace and code blocks
        if code.startswith("py\n"):
            code = code[3:]

        try:
            # add a layer of indentation
            cmd = "\n    ".join(code.splitlines())

            # wrap in async def body
            body = f"async def {fn_name}():\n    {cmd}"

            parsed = ast.parse(body)
            body = parsed.body[0].body

            insert_returns(body)

            env = {
                "bot": self.bot,
                "ctx": ctx,
                "message": ctx.message,
                "server": ctx.message.guild,
                "channel": ctx.message.channel,
                "author": ctx.message.author,
                "commands": commands,
                "discord": discord,
                "guild": ctx.message.guild,
            }
            env.update(globals())

            exec(compile(parsed, filename="<ast>", mode="exec"), env)

            result = await eval(f"{fn_name}()", env)

            out = ">>> " + code + "\n"
            output = "```py\n{}\n\n{}```".format(out, result)

            if len(output) > 2000:
                await ctx.send("The output is too long?")
            else:
                await ctx.send(output.format(result))
        except Exception as e:
            await ctx.send("```py\n>>> {}\n\n\n{}```".format(code, e))
                

async def setup(bot):
    await bot.add_cog(Owner(bot))
