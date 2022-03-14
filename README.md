# albedo-bot


# Setup
*Development is currently being done from the afk-image-processing Devcontainer
located [here]() that automatically sets up the development/execution environment
for **afk-image-processing** as well as **albedo-bot***
```bash
pip3 install -r /workspace/albedo-bot/requirements.txt
```
# Running the Bot
```bash
TOKEN=<discord bot token> python3 albedo_bot/albedo_main.py
```

## Database
Used to generate a PostgreSQL Database with initial data for the bot
```bash
python3 albedo_bot/database/create_db.py
```