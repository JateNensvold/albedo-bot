from .config import token, database_name, VERBOSE
from .json_config import (
    permissions, database, prefixes, blacklist)

from .json_config import (
    AFK_HELPER_PATH, BLACKLIST_JSON_PATH, CONFIG_FOLDER_PATH, DATABASE_JSON_PATH,
    GUILD_JSON_PATH, HERO_ALIAS_JSON_PATH, HERO_JSON_PATH, PERMISSIONS_JSON_PATH,
    PREFIX_JSON_PATH, AFK_HELPER_IMAGE_PREFIX)

if token == "":
    if token is None or len(token) == 0:
        raise Exception(
            "Set 'token' Environment variable at before running bot")
