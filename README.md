# albedo-bot


## Setup
*Development is currently being done from the afk-image-processing Devcontainer
located [here](https://github.com/JateNensvold/afk_image_processing) that automatically sets up the development/execution environment
for **afk-image-processing** as well as **albedo-bot**, it is highly recommended to follow the instructions there to setup the developer environment. If you need to run this package alone, follow the instructions below*
```bash
pip3 install -r /workspace/albedo-bot/requirements.txt
```


### Run database creation
```bash
# Add albedo-bot token listed in the discord api developer portal to
# /workspace/albedo_bot/albedo_bot/config/config.py in the `token` field,
# or follow the commands printed on the screen from running one of the commands below


# To create a new database
cd /workspace/albedo-bot && python3 albedo_bot/albedo_main.py init
# To reinitialize a database
cd /workspace/albedo-bot && python3 albedo_bot/albedo_main.py reset
```

```
cd /workspace/afk_image_processing && python3 image_processing/build_db.py
```

## Running the Bot
```bash
python3 albedo_bot/albedo_main.py
```
