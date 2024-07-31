import discord
from discord.ext import commands

import json
import os

import modules.localAPIs.database as DbLib
import modules.helpers as helpers

class LangageHandler:
    def __init__(self):
        self.languages = {}
        
        for file in os.listdir("assets/language_data"):
            if file.endswith(".json5"):
                with open(f"assets/language_data/{file}", "r") as f:
                    json5_str = f.read()
                    json5_str = helpers.json5_to_json(json5_str)
                    
                    langauge = file.split(".")[0]
                    self.languages[langauge] = json.loads(json5_str)
    
    def get_user_language(
        self,
        userID: int = None,
        interaction: discord.Interaction = None
    ) -> str:
        language: str = None
        
        if userID is None and interaction:
            userID = interaction.user.id
        
        if userID:
            language = DbLib.language_table.read_value(userID)
        
        if language is None and \
        interaction is not None and \
        interaction.locale.value in self.languages:
            language = interaction.locale.value
        
        # if the user isn't using a supported language, default to english
        if language not in self.languages:
            language = "en-GB" # for testing purposes
        
        return language
    
    def tr(
        self,
        key: str,
        userID: int = None,
        interaction: discord.Interaction = None,
        language: str = None,
        **kwargs
    ) -> str:
        """
            TODO
            if the user is in the database, the interaction should only be used to get the user ID
            only resort to the client's locale if the user isn't stored
            
            all slash commands should use the interaction
            all text commands should use the userID
            
            the language paramater should be avoided, only really meant for debugging purposes
        """

        language = self.get_user_language(userID=userID, interaction=interaction)
        
        translation = self.languages[language].get(key, None)
        if translation is None:
            translation = self.languages["en-GB"].get(key, f"missing translation for translation key: `{key}`")
        
        return translation.format(**kwargs)

    async def tr_send(
        self,
        ctx: commands.Context,
        key: str,
        userID: int = None,
        interaction: discord.Interaction = None,
        language: str = None,
        **kwargs
    ) -> discord.Message:
        if userID is None:
            userID = ctx.author.id
        
        return await ctx.send(
            self.tr(
                key, userID=userID,
                interaction=interaction, language=language,
                **kwargs
            )
        )
    
    async def tr_reply(
        self,
        ctx: commands.Context,
        key: str,
        userID: int = None,
        interaction: discord.Interaction = None,
        language: str = None,
        **kwargs
    ) -> discord.Message:
        if userID is None:
            userID = ctx.author.id
        
        return await ctx.reply(
            self.tr(
                key, userID=userID,
                interaction=interaction, language=language,
                **kwargs
            )
        )


if __name__ == "__main__":
    language = LangageHandler()
    print(language.tr("beaver"))
    