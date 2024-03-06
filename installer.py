import threading
import subprocess
import shutil
import os
import time

if os.getenv('SUDO_USER'):
    print("--------------------------------------")
    print("DO NOT RUN THIS WITH SUDO\nuser: ", os.getenv('SUDO_USER'))
    print("--------------------------------------")
    print("exiting...")
    print("--------------------------------------")
    exit()

try:
    subprocess.run(["screen", "-v"])
except:  # noqa: E722
    print("`screen` isn't installed, please to install it using your distro's package manager")
    exit()

try:
    subprocess.run(["ffmpeg", "-version"])
except:  # noqa: E722
    print("`ffmpeg` isn't installed, please to install it using your distro's package manager")
    exit()

def log(output):
    print(f"-----------\n\n{output}\n")

HOME = os.path.expanduser('~')
LOCAL_PATH = os.path.dirname(os.path.realpath(__name__))

log("patching up service file for this system")
with open("misc/hatsune-miku.service", "r") as f:
    content = f.read()
    # replace META_INSTALL_PATH with the file this file is installed
    content = content.replace("META_INSTALL_PATH", LOCAL_PATH)

with open("misc/hatsune-miku.service", "w") as f:
    f.write(content)

log("creating virtual environment")
subprocess.run(["python3", "-m", "venv", "venv/"], check=True)
subprocess.run(["./venv/bin/pip", "install", "-r", "requirements.txt"], check=True)

log("creating folders")
os.makedirs("logs", exist_ok=True)
os.makedirs("assets/music", exist_ok=True)
os.makedirs("assets/audio", exist_ok=True)
os.makedirs("assets/videos", exist_ok=True)
os.makedirs("assets/images", exist_ok=True)
os.makedirs(f"{HOME}/.config/systemd/user", exist_ok=True)

log("copying files")
if not os.path.exists("config.json"):
    shutil.copy("config_example.json", "config.json")
if not os.path.exists(f"{HOME}/.config/systemd/user/hatsune-miku.service"):
    shutil.copy("misc/hatsune-miku.service", f"{HOME}/.config/systemd/user/hatsune-miku.service")

log("""DO NOT CLOSE THIS TERMINAL YET, we're still downloading stuff in the background
    Please open a new tab or window, and fill in config.json, then run `systemctl --user enable --now hatsune-miku.service` to start the bot :3""")

time.sleep(5)

log("starting download of hatsune miku songs in the background")
def download_songs():
    os.chdir("assets/music")
    subprocess.run(["../.././venv/bin/python", "-m", "spotdl", "https://open.spotify.com/playlist/37i9dQZF1DWZipvLjDtZYe"], stdout=subprocess.DEVNULL)

# start downloading spotify songs on a different thread
yt_dlp_thread = threading.Thread(target=download_songs)
yt_dlp_thread.start()