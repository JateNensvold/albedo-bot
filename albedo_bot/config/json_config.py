from albedo_bot.utils.permissions import Permissions
from albedo_bot.database.database import Database
from albedo_bot.utils.config import Config

from .json_configs import (
    PERMISSIONS_JSON_PATH, DATABASE_CONFIG_JSON_PATH, PREFIX_JSON_PATH,
    BLACKLIST_JSON_PATH, HERO_ALIAS_JSON_PATH, HERO_JSON_PATH)

permissions = Permissions.from_json(PERMISSIONS_JSON_PATH.resolve())
database_config = Config(DATABASE_CONFIG_JSON_PATH.resolve())
database = Database.from_json(database_config)
hero_data = Config(HERO_JSON_PATH.resolve())
prefixes = Config(PREFIX_JSON_PATH.resolve())
blacklist = Config(BLACKLIST_JSON_PATH.resolve())
hero_alias = Config(HERO_ALIAS_JSON_PATH.resolve())
