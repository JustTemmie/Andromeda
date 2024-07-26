to setup Andromeda on your own, copy the config_example.json file to a file name config.json then fill in the values, not all keys are required but certain commands will crash the bot if you for example don't have a tenor key

you will also need ffmpeg and poppler installed in your path, on debian-based distros this can be done with `sudo apt install ffmpeg poppler`

create a virtual environment for the bot `python -m venv venv/` on linux

install the required libraries `./venv/bin/python -m pip install -r requirements.txt`

then run the bot with `./venv/bin/python main.py`



there's an example systemd service file in the misc folder if you wish to set it up as a permanent bot
