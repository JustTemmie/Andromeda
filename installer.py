import threading
import subprocess
import shutil
import os


if os.getenv('SUDO_USER'):
    print("--------------------------------------")
    print("DO NOT RUN THIS WITH SUDO\nuser: ", os.getenv('SUDO_USER'))
    print("--------------------------------------")
    print("exiting...")
    print("--------------------------------------")
    exit()

try:
    subprocess.run(["screen", "-v"])
except:
    print("`screen` isn't installed, please to install it using your distro's package manager")
    exit()

try:
    subprocess.run(["ffmpeg", "-v"])
except:
    print("`ffmpeg` isn't installed, please to install it using your distro's package manager")
    exit()

def log(output):
    print(f"-----------\n{output}\n")

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
subprocess.run(["./venv/bin/python3", "-m", "pip", "install", "-r", "requirements.txt"], check=True)

log("creating folders")
os.makedirs("logs", exist_ok=True)
os.makedirs("assets/music", exist_ok=True)
os.makedirs("assets/audio", exist_ok=True)
os.makedirs("assets/videos", exist_ok=True)
os.makedirs("assets/images", exist_ok=True)
os.makedirs(f"{HOME}/.config/systemd/user", exist_ok=True)

log("copying files")
shutil.copy("config_example.json", "config.json")
shutil.copy("misc/hatsune-miku.service", f"{HOME}/.config/systemd/user/hatsune-miku.service")

log("starting download of hatsune miku songs in the background")
def run_yt_dlp():    
    subprocess.run(["./venv/bin/python", "misc/music_downloader.py", "https://www.youtube.com/playlist?list=PLYVt6sUD_amTtozqHuhl0uPs2oy34HQLm", "assets/music"], stdout=subprocess.DEVNULL)

# start the yt-dlp script on a different thread
yt_dlp_thread = threading.Thread(target=run_yt_dlp)
yt_dlp_thread.start()


log("""DO NOT CLOSE THIS TERMINAL YET, we're still downloading stuff in the background
    Please open a new tab or window, and fill in config.json, then run `systemctl --user enable --now hatsune-miku.service`""")