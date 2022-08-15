import os

_par_dir = os.path.abspath(os.path.dirname(__file__))
CONFIG_FOLDER_PATH = _par_dir

PERMISSIONS_JSON_PATH = os.path.join(
    CONFIG_FOLDER_PATH, "permissions_config.json")
DATABASE_CONFIG_JSON_PATH = os.path.join(
    CONFIG_FOLDER_PATH, "database_config.json")
HERO_JSON_PATH = os.path.join(CONFIG_FOLDER_PATH, "hero_data.json")
GUILD_JSON_PATH = os.path.join(CONFIG_FOLDER_PATH, "guild_config.json")
HERO_ALIAS_JSON_PATH = os.path.join(CONFIG_FOLDER_PATH, "hero_alias.json")
AFK_HELPER_PATH = os.path.join(_par_dir, "afk_helper")
PREFIX_JSON_PATH = os.path.join(_par_dir, "prefixes.json")
BLACKLIST_JSON_PATH = os.path.join(_par_dir, "blacklist.json")
AFK_HELPER_IMAGE_PREFIX = os.path.join(_par_dir, "albedo_bot")
