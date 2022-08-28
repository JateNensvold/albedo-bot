import os
from pathlib import Path

_json_configs_path = Path(__file__).parent
_config_path = _json_configs_path.parent
_albedo_bot_modules_path = _config_path.parent
_albedo_bot_utils_path = _albedo_bot_modules_path.joinpath("utils")
JSON_CONFIG_FOLDER_PATH = _json_configs_path

PERMISSIONS_JSON_PATH = JSON_CONFIG_FOLDER_PATH.joinpath(
    "permissions_config.json")
DATABASE_CONFIG_JSON_PATH = JSON_CONFIG_FOLDER_PATH.joinpath(
    "database_config.json")
HERO_JSON_PATH = JSON_CONFIG_FOLDER_PATH.joinpath("hero_data.json")
# Currently not used
GUILD_JSON_PATH = JSON_CONFIG_FOLDER_PATH.joinpath("guild_config.json")
HERO_ALIAS_JSON_PATH = JSON_CONFIG_FOLDER_PATH.joinpath("hero_alias.json")
AFK_HELPER_PATH = _albedo_bot_utils_path.joinpath("afk_helper")
PREFIX_JSON_PATH = JSON_CONFIG_FOLDER_PATH.joinpath("prefixes.json")
BLACKLIST_JSON_PATH = JSON_CONFIG_FOLDER_PATH.joinpath("blacklist.json")
AFK_HELPER_IMAGE_PREFIX = AFK_HELPER_PATH.joinpath("public")
AFK_HELPER_IMAGE_DIRECTORY = AFK_HELPER_IMAGE_PREFIX.joinpath("img")
AFK_HELPER_PORTRAITS_DIRECTORY = AFK_HELPER_IMAGE_DIRECTORY.joinpath(
    "portraits")
