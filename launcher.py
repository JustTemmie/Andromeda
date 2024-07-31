import os
import config

# create some folders what are required for a first run
directories_to_make = [
    "local_only",
    "assets",
    "assets/music",
    "assets/audio",
    "assets/videos",
    "assets/images",
    "assets/misc",
    "assets/language_data",
]
directories_to_empty = ["temp", "logs"]

files_to_make = {
    "local_only/yrIDs.json": "{}"
}

for path in directories_to_make + directories_to_empty:
    if not os.path.exists(path):
        print(f'creating folders at: "{path}"')
        os.mkdir(path)

for path, content in files_to_make.items():
    if not os.path.exists(path):
        print(f'creating file at: "{path}" with content: "{content}"')
        with open(path, "w") as f:
            f.write(content)
    
        
if config.DEVELOPMENT:
    for dir in directories_to_empty:
        for file in os.listdir(dir):
            os.remove(f"{dir}/{file}")
            

import modules.localAPIs.language as languageLib
lang = languageLib.LangageHandler()

if __name__ == "__main__":
    import asyncio
    import main
    
    main.bot.loop = asyncio.new_event_loop()
    asyncio.set_event_loop(main.bot.loop)
    asyncio.run(main.init())