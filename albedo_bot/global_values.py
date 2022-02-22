import os
import json
from typing import Dict
from albedo_bot.database.database import Database
from albedo_bot.commands.helpers.permissions import Permissions


par_dir = os.path.dirname(__file__)

CONFIG_FOLDER_PATH = os.path.join(par_dir, "config")

PERMISSIONS_JSON_PATH = os.path.join(CONFIG_FOLDER_PATH, "permissions_config.json")
DATABASE_JSON_PATH = os.path.join(CONFIG_FOLDER_PATH, "database_config.json")
HERO_JSON_PATH = os.path.join(CONFIG_FOLDER_PATH, "heroSkills.json")
GUILD_JSON_PATH = os.path.join(CONFIG_FOLDER_PATH, "guild_config.json")


PERMISSIONS_DATA: Dict = None
DATABASE_DATA: Dict = None
DATABASE: Database = None

with open(DATABASE_JSON_PATH, "r", encoding="utf-8") as file:
    DATABASE_DATA = json.load(file)
    DATABASE = Database(DATABASE_DATA["user"], DATABASE_DATA["password"],
                        DATABASE_DATA["address"])

with open(PERMISSIONS_JSON_PATH, "r", encoding="utf-8") as file:
    PERMISSIONS_DATA = json.load(file)
    for role_name, role_data in PERMISSIONS_DATA:
        Permissions(role_name, role_data["names"],
                    role_data["roles"], role_data["priority"])
