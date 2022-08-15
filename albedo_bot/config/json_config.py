from albedo_bot.utils.permissions import Permissions
from albedo_bot.database.database import Database
from albedo_bot.utils.config import Config

from .json_configs import (
    PERMISSIONS_JSON_PATH, DATABASE_CONFIG_JSON_PATH, PREFIX_JSON_PATH,
    BLACKLIST_JSON_PATH, HERO_ALIAS_JSON_PATH)

permissions = Permissions.from_json(PERMISSIONS_JSON_PATH)
database_config = Config(DATABASE_CONFIG_JSON_PATH)
database = Database.from_json(database_config)
prefixes = Config(PREFIX_JSON_PATH)
blacklist = Config(BLACKLIST_JSON_PATH)
hero_alias = Config(HERO_ALIAS_JSON_PATH)
