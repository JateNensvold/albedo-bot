import os
import shutil

from .json_config import (
    permissions, database, prefixes, blacklist, hero_alias)
from .json_config import (
    AFK_HELPER_PATH, AFK_HELPER_IMAGE_PREFIX, BLACKLIST_JSON_PATH,
    CONFIG_FOLDER_PATH, DATABASE_JSON_PATH, GUILD_JSON_PATH,
    HERO_ALIAS_JSON_PATH, HERO_JSON_PATH, PERMISSIONS_JSON_PATH,
    PREFIX_JSON_PATH)

cur_dir = os.path.abspath(os.path.dirname(__file__))
if "config.py" not in os.listdir(cur_dir):
    shutil.copyfile(os.path.join(cur_dir, "default_config.py"),
                    os.path.join(cur_dir, "config.py"))
# autopep8: off
from .config import (
    token, database_name,
    VERBOSE, processing_server_address) # pylint: disable=wrong-import-position

if token == "":
    if token is None or len(token) == 0:
        raise Exception(
            "Set 'token' Environment variable at "
            f"({os.path.join(cur_dir, 'config.py')}) before running bot")
