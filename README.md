# wgcompany-telegram-bot

Installation:

1) Create a virtual environment and install the necessary packages:
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2) Create a `secrets.yml` file with the following content:
```
---
telegram:
  bot_token: <your bot token>
  chat_id: <your telegram ID>
...
```

To find out your telegram chat ID, send a message to @RawDataBot.

3) Run and detach the script: `nohup python3 run.py &`