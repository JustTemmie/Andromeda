import discord
from discord.ext import commands

import modules.helpers as helpers
from launcher import lang

class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        bot.remove_command("help")
                
        
        self.page_order = [
            "main",
            "economy",
            "admin",
            "beta"
        ]
        
        self.page_emojis = {
            "main": "❓",
            "economy": "💰",
            "admin": "🛡️",
            "beta": "✨",
            None: "🪄"
        }

    def get_page_name(self, page_ID: str, userID: int):
        return lang.tr(f"help_command_page_{page_ID}", userID = userID)
    
    def get_page_emoji(self, page_ID):
        return self.page_emojis.get(page_ID, self.page_emojis[None])

    def get_page_description(self, pageID: str, userID: int):
        return lang.tr(f"help_command_page_description_{pageID}", userID=userID)
    
    def set_page_content(self, embed: discord.Embed, page_number: int, command_pages, userID: int) -> discord.Embed:
        page: dict[list[dict[list]]] = command_pages[page_number]
                    
        page_emoji = self.get_page_emoji(page["ID"])
        page_name = self.get_page_name(page["ID"], userID)
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
        brief="command_brief_help",
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
            await lang.tr_send(ctx, "help_command_missing_command", command=command)
            return
        
        if command_data.hidden:
            embed = helpers.create_embed(ctx)
            embed.title = lang.tr("help_command_hidden_command_title", userID=ctx.author.id)
            embed.description = lang.tr("help_command_hidden_command_description", userID=ctx.author.id)
            await ctx.send(embed=embed)
            return

        if not await helpers.can_run(ctx, command_data):
            embed = helpers.create_embed(ctx)
            embed.title = command_data.name
            embed.description = lang.tr("help_command_invalid_permissions", userID=ctx.author.id)
            await ctx.send(embed=embed)
            return
        
        embed = helpers.create_embed(ctx)
        embed.title = command_data.name
        
        if command_data.brief:
            embed.description = lang.tr(command_data.brief, userID=ctx.author.id)
        
        if command_data.description:
            embed.add_field(
                name=lang.tr("help_command_command_description", userID=ctx.author.id),
                value=lang.tr(command_data.description, userID=ctx.author.id),
                inline=False
            )
        
        if command_data.aliases:
            embed.add_field(
                name=lang.tr("help_command_command_aliases", userID=ctx.author.id),
                value=", ".join(command_data.aliases),
                inline=False
            )
            
        embed.add_field(
            name=lang.tr("help_command_command_signature", userID=ctx.author.id),
            value=f"{ctx.prefix}{command_data.name} {command_data.signature}",
            inline=False
        )

        if command_data.cooldown:
            value = self.bot.lang
            embed.add_field(
                name=lang.tr(
                    "help_command_command_cooldown",
                    userID=ctx.author.id,
                    times=command_data.cooldown.rate,
                    duration=command_data.cooldown.per
                ),
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
                    label=self.get_page_name(page["ID"], ctx.author.id),
                    value=page_number,
                    emoji=self.get_page_emoji(page["ID"]),
                    description=self.get_page_description(page["ID"], userID=ctx.author.id)
                ))
        
        
        embed = helpers.create_embed(ctx)
        self.set_page_content(embed, 0, command_pages, ctx.author.id)
        
        # function to be called when the user tries to switch pages
        async def set_page_callback(interaction: discord.interactions.Interaction):
            if interaction.user != ctx.author:
                await interaction.response.defer()
                return
            
            new_page_index = int(select_page_list.values[0])
            
            self.set_page_content(embed, new_page_index, command_pages, interaction.user.id)

            await msg.edit(embed=embed)
            await interaction.response.defer()
        
        
        view = discord.ui.View()
        if len(page_options) > 1:
            select_page_list = discord.ui.Select(
                placeholder=lang.tr("help_command_change_page_placeholder", userID=ctx.author.id),
                options=page_options
            )
            select_page_list.callback = set_page_callback
            view.add_item(select_page_list)

        msg = await ctx.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(Help(bot))
