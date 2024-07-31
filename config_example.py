
API_KEYS = {
    "DISCORD": "TOKEN",
    "TENOR":  "KEY"
}

IDENTIFIERS = {
    "TENOR": "default-identity-key"
}

COMMAND_DEFAULTS = {
    "WEATHER_LOCATION": "Stockholm"
}

PREFIXES= ["a!"]
# these three all contain discord IDs, not mandatory
OWNER_IDS= []
HOST_OWNERS= []
TRUSTED_IDS= []
# if you wish to provide a whitelist of allowed cogs, this might be nice if you only want this as a music bot for example
COG_LIST_OVERWRITES = []
STATUS_OVERWRITES = []

SHARDS = 1
SYNC_TREE = True
DEVELOPMENT = False
# irrelevant if the bot isn't in development mode
DEVELOPMENT_GUILD = 1016777760305320036
