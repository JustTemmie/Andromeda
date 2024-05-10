import json

def getConfig():
    with open("config.json", "r") as f:
        return json.load(f)

def getSettings():
    with open("settings.json", "r") as f:
        return json.load(f)