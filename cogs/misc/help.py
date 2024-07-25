import discord
from discord.ext import commands

import modules.helpers as helpers
import modules.decorators as decorators
import modules.localAPIs.database as DbLib
import modules.APIs.tenor as tenorLib

class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
        self.page_order = [
            "main",
            "economy",
            "admin",
            "beta"
        ]
        
        self.page_names = {
            "main": "Main Page",
            "economy": "Economy Page",
            "beta": "Beta Page",
            "admin": "Administator Page",
        }
        
        self.page_emojis = {
            "main": "❓",
            "economy": "💰",
            "admin": "🛡️",
            "beta": "✨",
            None: "🪄"
        }
        
        self.page_decriptions = {
            "main": "The main commands",
            "economy": "Economy related commands",
            "beta": "Commands in active development, expect bugs!",
            "admin": "Commands with higher permission requirements",
            None: "No description provided"
        }
    
    def get_page_name(self, page_ID):
        return self.page_names.get(page_ID, f"{page_ID.title()} Page")
    
    def get_page_emoji(self, page_ID):
        return self.page_emojis.get(page_ID, self.page_emojis[None])

    def get_page_description(self, page_ID):
        return self.page_decriptions.get(page_ID, self.page_decriptions[None])
    
    def set_page_content(self, embed: discord.Embed, page_number: int, command_pages) -> discord.Embed:
        page: dict[list[dict[list]]] = command_pages[page_number]
                    
        page_emoji = self.get_page_emoji(page["ID"])
        page_name = self.get_page_name(page["ID"])
        embed.title = f"{page_emoji} {page_name}"
        while len(embed.fields) > 0:
            embed.remove_field(0)
        
        for category in page["categories"]:
            embed.add_field(
                name=category["ID"].title(),
                value=f'`{", ".join(command_data["name"] for command_data in category["commands"])}`',
                inline=False
            )
        
        return embed

    @commands.command(
        name="help", aliases=["how??"],
        brief="hey you're using it correctly!",
        extras={"page": "main", "category":"info"}
    )
    async def help_command(self, ctx: commands.Context, command: str = None):
        if command:
            await self.help_command_info(ctx, command)
        
        else:
            await self.help_menu(ctx)
    
    async def help_command_info(self, ctx: commands.Context, command: str):
        command_data = self.bot.get_command(command)
        
        if not command_data:
            await ctx.send(f"sorry, i can't seem to find any commands named `{command}`")
            return
        
        if command_data.hidden:
            embed = helpers.create_embed(ctx)
            embed.title = "Hidden Command"
            embed.description = "sorry, i can't tell you anything about that one, it's a secret"
            await ctx.send(embed=embed)
            return

        if not await helpers.can_run(ctx, command_data):
            embed = helpers.create_embed(ctx)
            embed.title = command_data.name
            embed.description = "sorry, you don't have the permissions required to run this command"
            await ctx.send(embed=embed)
            return
        
        embed = helpers.create_embed(ctx)
        embed.title = command_data.name
        
        if command_data.brief:
            embed.description = command_data.brief
        
        if command_data.description:
            embed.add_field(
                name="In depth description",
                value=command_data.description,
                inline=False
            )
        
        if command_data.aliases:
            embed.add_field(
                name="Aliases",
                value=", ".join(command_data.aliases),
                inline=False
            )
            
        embed.add_field(
            name="Usage",
            value=f"{ctx.prefix}{command_data.name} {command_data.signature}",
            inline=False
        )

        if command_data.cooldown:
            value = f"{command_data.cooldown.rate} times per {command_data.cooldown.per} seconds"
            embed.add_field(
                name="Cooldown",
                value=f"{value}",
                inline=False
            )
            
        await ctx.send(embed=embed)
    
    
    async def help_menu(self, ctx: commands.Context):
        command_list = self.bot.commands
        
        hidden_commands = 0
        command_pages: list[dict[list[dict[list[commands.Command]]]]] = []
        
        for page_ID in self.page_order:
            command_pages.append({
                "ID": page_ID,
                "categories": []
            })
        
        for command in command_list:
            if not await helpers.can_run(ctx, command):
                hidden_commands += 1
            
            else:
                command_page_ID: str = command.extras.get("page", "main")
                command_category: str = command.extras.get("category", "uncategorized")
                
                page_index = 0
                for i, page in enumerate(command_pages):
                    if page["ID"] == command_page_ID:
                        page_index = i
                        break
                else:
                    page_index = len(command_pages)
                    command_pages.append({
                        "ID": command_page_ID,
                        "categories": []
                    })
                
                category_index = 0
                for i, category in enumerate(command_pages[page_index]["categories"]):
                    if command_category == category["ID"]:
                        category_index = i
                        break
                else:
                    category_index = len(command_pages[page_index]["categories"])
                    command_pages[page_index]["categories"].append({
                        "ID": command_category,
                        "commands": []
                    })
                
                
                command_data = {}
                command_data["name"] = command.name
                command_data["hidden"] = command.hidden
                # command_data["brief"] = command.brief
                # command_data["usage"] = command.usage
                # command_data["aliases"] = command.aliases
                
                command_pages[page_index]["categories"][category_index]["commands"].append(command_data)
        
        # sort the categories and the commands within them alphabetically
        for page in command_pages:
            page["categories"].sort(key=lambda x: x["ID"])
            for category in page["categories"]:
                category["commands"].sort(key=lambda x: x["name"])
        
        page_options: list[discord.SelectOption] = []
        for page_number, page in enumerate(command_pages):
            if len(page["categories"]) > 0:
                page_options.append(discord.SelectOption(
                    label=self.get_page_name(page["ID"]),
                    value=page_number,
                    emoji=self.get_page_emoji(page["ID"]),
                    description=self.get_page_description(page["ID"])
                ))
        
        
        embed = helpers.create_embed(ctx)
        self.set_page_content(embed, 0, command_pages)
        
        # function to be called when the user tries to switch pages
        async def set_page_callback(interaction: discord.interactions.Interaction):
            if interaction.user != ctx.author:
                await interaction.response.defer()
                return
            
            new_page_index = int(select_page_list.values[0])
            
            self.set_page_content(embed, new_page_index, command_pages)

            await msg.edit(embed=embed)
            await interaction.response.defer()
        
        
        view = discord.ui.View()
        if len(page_options) > 1:
            select_page_list = discord.ui.Select(placeholder="Change the current page", options=page_options)
            select_page_list.callback = set_page_callback
            view.add_item(select_page_list)

        msg = await ctx.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(Help(bot))
