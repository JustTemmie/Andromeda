import discord
from discord.ext import commands
from discord import app_commands

from datetime import datetime, timedelta
import dateutil.easter as easter

import random

if __name__ == "__main__":
    import sys
    sys.path.append(".")

import modules.localAPIs.database as DbLib
import modules.generic_helpers as generic_helpers
import settings
from objects import lang

random.seed((datetime.now() - datetime(1970, 1, 1)).days)
current_year = 2024

daily_events = {
    "red_panda": {
        "date": generic_helpers.get_red_panda_day(current_year),
        "extra_coins": random.randint(10, 30) * 25,
    },
    "easter": {
        "date": easter.easter(current_year),
    },
    "pancake": {
        "date": easter.easter(current_year) - timedelta(days=47),
        "extra_coins": random.randint(7, 10) * 100,
    },
    "waffle": {
        "date": datetime(current_year, 25, 3).date(),
        "extra_coins": random.randint(7, 10) * 100,
    },
    "new_years": {
        "date": datetime(current_year, 1, 1).date(),
        "coin_multiplier": 3,
        "extra_coins": 5000
    },
    "valentines": {
        "date": datetime(current_year, 14, 2).date(),
    },
    "pi": {
        "date": datetime(current_year, 14, 3).date(),
        "extra_coins": 314
    },
    "ice_cream": {
        "date": datetime(current_year, 1, 7).date(),
        "extra_coins": 500
    },
    "mango": {
        "date": datetime(current_year, 22, 7).date(),
        "extra_coins": 500
    },
    "st_patrick": {
        "date": datetime(current_year, 17, 3).date(),
        "extra_coins": random.randint(10, 30) * 25,
    },
    "international_beaver": {
        "date": datetime(current_year, 7, 4).date(),
        "extra_logs": 2500,
    },
    "halloween": {
        "date": datetime(current_year, 1, 1).date(),
        "coin_multiplier": 5,
        "extra_coins": 2500
    },
}

random.seed()

async def daily_command(userID) -> str:
    # DbLib.economy_database.
    today = datetime.today().date()
    for ID, event in daily_events.items():
        print(event["date"], today)
        if event["date"] == today:
            print("yay!!")
            print(lang.tr(f"daily_event_{ID}_message"))


async def setup(bot):
    pass

if __name__ == "__main__":
    import asyncio
    asyncio.run(daily_command(292929))