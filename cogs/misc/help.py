import discord
from discord.ext import commands

import modules.helpers as helpers
import modules.decorators as decorators
import modules.database as DbLib
import modules.APIs.tenor as tenorLib

class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
        # emojis to go with the page names, page names default to None
        self.page_emojis = {
            "main": "❓",
            "economy": "💰",
            None: "🫨"
        }

    @commands.command(
        name="help", aliases=["how??"],
        extras={"page": "main", "category":"info"}
    )
    async def help_command(self, ctx: commands.Context):
        command_list = self.bot.commands
        
        hidden_commands = 0
        commands_by_page_and_category: dict[dict[list[dict]]] = {}
        
        for command in command_list:
            if not await helpers.can_run(ctx, command):
                hidden_commands += 1
            
            else:
                page: str = command.extras.get("page", "main")
                category: str = command.extras.get("category", "undefined")
                
                if page not in commands_by_page_and_category.keys():
                    commands_by_page_and_category[page] = {}
                    
                if category not in commands_by_page_and_category[page].keys():
                    commands_by_page_and_category[page][category] = []
                    
                command_data = {}
                command_data["name"] = command.name
                command_data["hidden"] = command.hidden
                command_data["brief"] = command.brief
                command_data["usage"] = command.usage
                command_data["aliases"] = command.aliases
                
                commands_by_page_and_category[page][category].append(command_data)
        
        for page_ID in commands_by_page_and_category:
            for category in commands_by_page_and_category[page_ID].values():
                category = sorted(category, key=lambda command: command["name"])
        
        embed = helpers.create_embed(ctx)
        page_index = list(commands_by_page_and_category.keys())[0]
        page: dict[list[dict]] = commands_by_page_and_category[page_index]
        for category_name, command_list in page.items():
            embed.add_field(
                name=category_name.title(),
                value=f'`{", ".join(command_data["name"] for command_data in command_list)}`',
                inline=False
            )
        
        await ctx.send(embed=embed)
        

async def setup(bot):
    await bot.add_cog(Help(bot))
