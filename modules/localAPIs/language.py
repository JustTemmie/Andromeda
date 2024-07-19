import json
import os
import discord
import re

class LangageHandler:
    def __init__(self):
        self.languages = {}
        
        # some regexes to remove comments and trailing commas
        def to_json5(json5_str):
            json5_str = re.sub(r'//.*', '', json5_str)
            json5_str = re.sub(r'/\*.*?\*/', '', json5_str, flags=re.DOTALL)
            
            json5_str = re.sub(r',\s*([}\]])', r'\1', json5_str)
            return json5_str

        
        for file in os.listdir("assets/language_data"):
            if file.endswith(".json5"):
                with open(f"assets/language_data/{file}", "r") as f:
                    json5_str = f.read()
                    json5_str = to_json5(json5_str)
                    
                    langauge = file.split(".")[0]
                    self.languages[langauge] = json.loads(json5_str)

    
    def tr(
        self,
        key,
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

        if userID is None and interaction:
            userID = interaction.user.id
        
        if userID:
            if userID == 616228691155877898:
                language = "fi"
            """
                TODO make a database and set the translation key within that
            """
            pass
        
        if language is None and \
        interaction and \
        interaction.locale in self.languages:
            language = interaction.locale
        
        # if the user isn't using a supported language, default to american english
        if language not in self.languages:
            language = "en-GB" # for testing purposes
        
        translation = self.languages[language].get(key, None)
        if translation is None:
            translation = self.languages["en-GB"].get(key, f"missing translation for translation key: `{key}`")
        
        return translation.format(**kwargs)

    async def tr_send(
        self,
        ctx,
        key,
        userID: int = None,
        interaction: discord.Interaction = None,
        language: str = None,
        **kwargs
    ) -> None:
        if userID is None:
            userID = ctx.author.id
        
        await ctx.send(
            self.tr(
                key, userID=userID,
                interaction=interaction, language=language,
                **kwargs
            )
        )
    
    async def tr_reply(
        self,
        ctx,
        key,
        userID: int = None,
        interaction: discord.Interaction = None,
        language: str = None,
        **kwargs
    ) -> None:
        if userID is None:
            userID = ctx.author.id
        
        await ctx.reply(
            self.tr(
                key, userID=userID,
                interaction=interaction, language=language,
                **kwargs
            )
        )


if __name__ == "__main__":
    language = LangageHandler()
    print(language.tr("beaver"))
    