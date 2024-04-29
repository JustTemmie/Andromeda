import random
import requests
import json

if __name__ == "__main__":
    import config as configLib
else:
    import hatsune_miku.APIs.config as configLib


tenor_key = configLib.getConfig()["API_KEYS"]["TENOR"]
ckey = "Hatsune-Miku-Discord-Bot"


def getGifs(query, limit):
    r = requests.get(
        f"https://tenor.googleapis.com/v2/search?q={query}&key={tenor_key}&client_key={ckey}&limit={limit}"
    )

    if r.status_code == 200:
        # load the GIFs using the urls for the smaller GIF sizes
        return json.loads(r.content)["results"]
    else:
        print(f"status code {r.status_code} met whilst trying to fetch gifs using the query {query}\n    ERROR: {r.text}")
        return []

def getRandomGifData(query, limit):
    gifs = getGifs(query, limit)

    return gifs[random.randrange(0, len(gifs))]

def getRandomGifLink(query, limit, format = "gif"):
    gif_data = getRandomGifData(query, limit)
    
    if format not in gif_data["media_formats"]:
        string = f"the format `{format}` is not a valid format for requesting Tenor gifs"
        print(string)
        return string
    
    return gif_data["media_formats"][format]["url"]

if __name__ == "__main__":
    print(getRandomGifLink("hatsune miku", 5, "webm"))