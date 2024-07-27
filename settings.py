# settings.py is different from config.py as these changes should actively be update with git

class Emojis:
    def __init__(self):
        self.coin = "<a:coin:1266553468064235590>"

STATUSES = [
    # listening to (x)
    "listening-🎵",
    "listening-your mommy, calling me siri",

    # watching (x)
    "watching-over {len(self.bot.users)} users",
    "watching-over {len(self.bot.guilds)} guilds",
    "watching-{random.choice(self.bot.users).display_name}",
    "watching-cats go nya",

    # playing (x)
    "playing-Amogus Meme Compilation 2 -2021-.mp4 at my local coop extra's speakers",
    "playing-with your heart <3",
    "playing-main.py",

    # cmopeting in (x)
    "competing-a fight for your heart <3",
    "competing-the Beaver Clicker World Finals"
]

emojis = Emojis()