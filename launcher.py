import modules.localAPIs.language as languageLib

lang = languageLib.LangageHandler()

if __name__ == "__main__":
    import asyncio
    import main
    
    main.bot.loop = asyncio.new_event_loop()
    asyncio.set_event_loop(main.bot.loop)
    asyncio.run(main.init())