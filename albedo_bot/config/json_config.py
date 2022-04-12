import os
from albedo_bot.config.permissions import Permissions
from albedo_bot.database.database import Database
from albedo_bot.utils.config import Config


_par_dir = os.path.abspath(os.path.dirname(__file__))
CONFIG_FOLDER_PATH = _par_dir

PERMISSIONS_JSON_PATH = os.path.join(
    CONFIG_FOLDER_PATH, "permissions_config.json")
DATABASE_JSON_PATH = os.path.join(CONFIG_FOLDER_PATH, "database_config.json")
HERO_JSON_PATH = os.path.join(CONFIG_FOLDER_PATH, "hero_data.json")
GUILD_JSON_PATH = os.path.join(CONFIG_FOLDER_PATH, "guild_config.json")
HERO_ALIAS_JSON_PATH = os.path.join(CONFIG_FOLDER_PATH, "hero_alias.json")
AFK_HELPER_PATH = os.path.join(_par_dir, "afk_helper")
PREFIX_JSON_PATH = os.path.join(_par_dir, "prefixes.json")
BLACKLIST_JSON_PATH = os.path.join(_par_dir, "blacklist.json")
AFK_HELPER_IMAGE_PREFIX = os.path.join(_par_dir, "abledo_bot")


permissions = Permissions.from_json(PERMISSIONS_JSON_PATH)
database = Database.from_json(DATABASE_JSON_PATH)
prefixes = Config(PREFIX_JSON_PATH)
blacklist = Config(BLACKLIST_JSON_PATH)
hero_alias = Config(HERO_ALIAS_JSON_PATH)
