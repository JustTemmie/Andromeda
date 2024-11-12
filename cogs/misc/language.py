import discord
from discord.ext import commands
from discord import app_commands

import os
import typing

if __name__ == "__main__":
    import sys
    sys.path.append(".")

import modules.database.user as userDB
from objects import lang

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
            current_language_ID = lang.get_user_language(ctx.author.id)
            current_language = self.get_language_friendly_name(current_language_ID)
            await lang.tr_send(
                ctx,
                "language_setter_current_language",
                userID=ctx.author.id,
                current_language=current_language
            )
            return

        if language not in valid_languages:
            await lang.tr_send(
                ctx, "language_setter_invalid_language",
                userID=ctx.author.id, new_language=language,
                valid_languages=", ".join(f'{ID} ({display_name})' for ID, display_name in language_friendly_names.items())
            )
            return

        success = self.set_database_value(ctx.author.id, language)
        
                
        if not success:
            await lang.tr_send(ctx, "language_setter_database_error")
            return
        
        new_language = f"{language} ({self.get_language_friendly_name(language)})"
        await lang.tr_send(ctx, "language_setter_success", new_language=new_language)
    
    
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
    @app_commands.describe(language="Your prefered language")
    async def language_slash_command(
        self, interaction: discord.Interaction,
        language: str = None
    ):
        if language is None:
            current_language_ID = lang.get_user_language(interaction.user.id)
            current_language = self.get_language_friendly_name(current_language_ID)
            await interaction.response.send_message(lang.tr(
                "language_setter_current_language",
                interaction=interaction, current_language=current_language
            ))
            return

        if language not in valid_languages:
            await interaction.response.send_message(
                lang.tr(
                    "language_setter_invalid_language",
                    interaction=interaction, new_language=language,
                    valid_languages=", ".join(f'{ID} ({display_name})' for ID, display_name in zip(valid_languages, language_friendly_names.values()))
                )
            )
            return

        success = self.set_database_value(interaction.user.id, language)
        
        if not success:
            await interaction.response.send_message(lang.tr("language_setter_database_error", interaction=interaction))
            return
        
        new_language = f"{language} ({self.get_language_friendly_name(language)})"
        await interaction.response.send_message(lang.tr("language_setter_success", interaction=interaction, new_language=new_language))
    
    def set_database_value(self, userID, new_language) -> bool:
        with userDB.Driver.SessionMaker() as db_session:
            user_query = db_session.query(userDB.User)
            user_query = user_query.where(userID == userDB.User.id)
            user = user_query.first()
            
            if not user:
                return False
            
            user.preferred_language = new_language
            db_session.commit()
            
            return True
    
    
    def get_language_friendly_name(self, languageID):
        return language_friendly_names.get(languageID, "None")


async def setup(bot):
    await bot.add_cog(Language(bot))
