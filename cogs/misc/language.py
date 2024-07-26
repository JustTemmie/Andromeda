import discord
from discord.ext import commands
from discord import app_commands

import os
import typing

if __name__ == "__main__":
    import sys
    sys.path.append(".")

import modules.localAPIs.database as DbLib
from launcher import lang

language_friendly_names = {
    "en-GB": "English",
    "en-US": "American English",
    # "da": "Danish",
    "fi": "Finnish",
    # "fr": "French",
    # "de": "German",
    "se": "Northern Sami",
    "no": "Norwegian (Bokmål)",
    "nn": "Norwegian (Nynorsk)",
    # "ru": "Russian",
    # "es-ES": "Spanish",
    # "sv-SE": "Swedish",
}

valid_languages = []

for file in os.listdir("assets/language_data"):
    if file.endswith(".json5"):
        valid_languages.append(file.split(".")[0])

class Language(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="language",
        brief="command_brief_language",
        extras={"page": "main", "category":"settings"}
    )
    async def language_text_command(self, ctx: commands.Context, *, language: str = None):
        if language is None:
            current_language_ID = DbLib.language_table.read_value(ctx.author.id)
            if current_language_ID:
                current_language = self.get_language_friendly_name(current_language_ID)
                await lang.tr_send(
                    ctx,
                    "language_setter_current_language",
                    userID=ctx.author.id,
                    current_language=current_language
                )
                return
            else:
                await lang.tr_send(
                    ctx,
                    "language_setter_no_language_set_text_command",
                    prefix=ctx.prefix,
                    command_name=ctx.invoked_with
                )
                return

        if language not in valid_languages:
            await lang.tr_send(
                ctx, "language_setter_invalid_language",
                userID=ctx.author.id, new_language=language,
                valid_languages=", ".join(f'{ID} ({display_name})' for ID, display_name in zip(valid_languages, language_friendly_names.values()))
            )
            return

        self.set_database_value(ctx.author.id, language)
        
        new_language = f"{language} ({self.get_language_friendly_name(language)})"
        await lang.tr_send(ctx, "language_setter_success", userID=ctx.author.id, new_language=new_language)
    
    
    async def language_autocomplete(self,
        interaction: discord.Interaction,
        current: str,
    ) -> typing.List[app_commands.Choice[str]]:
        languages = []
        
        for language_ID, language_display in language_friendly_names.items():
            if current.lower() in language_ID or current.lower() in language_display.lower():
                # doublecheck if it's a valid language
                if language_ID in valid_languages:
                    languages.append(app_commands.Choice(name=language_display, value=language_ID))

        if len(languages) > 25:
            languages = languages[:24]
            languages.append(app_commands.Choice(
                name=lang.tr("slash_command_autocomplete_too_many_values", interaction=interaction),
                value=None
            ))
        
        return languages
    
    @app_commands.command(
        name="language",
        description="set your preferred language"
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.autocomplete(language=language_autocomplete)
    async def language_slash_command(
        self, intercation: discord.Interaction,
        language: str = None
    ):
        if language is None:
            current_language_ID = DbLib.language_table.read_value(intercation.user.id)
            if current_language_ID:
                current_language = self.get_language_friendly_name(current_language_ID)
                await intercation.response.send_message(lang.tr(
                    "language_setter_current_language",
                    intercation=intercation, current_language=current_language
                ))
                return
            else:
                await intercation.response.send_message(lang.tr(
                    "language_setter_no_language_set_slash_command",
                    intercation=intercation,
                ))
                return

        if language not in valid_languages:
            await intercation.response.send_message(
                lang.tr(
                    "language_setter_invalid_language",
                    intercation=intercation, new_language=language,
                    valid_languages=", ".join(f'{ID} ({display_name})' for ID, display_name in zip(valid_languages, language_friendly_names.values()))
                )
            )
            return

        self.set_database_value(intercation.user.id, language)
        
        new_language = f"{language} ({self.get_language_friendly_name(language)})"
        await intercation.response.send_message(lang.tr("language_setter_success", intercation=intercation, new_language=new_language))
    
    def set_database_value(self, userID, new_language) -> str:
        if DbLib.language_table.read_value(userID):
            DbLib.language_table.update(userID, "preferred_language", new_language)

        else:
            DbLib.language_table.write(userID, new_language)
    
    
    def get_language_friendly_name(self, languageID):
        return language_friendly_names.get(languageID, "None")


async def setup(bot):
    await bot.add_cog(Language(bot))
