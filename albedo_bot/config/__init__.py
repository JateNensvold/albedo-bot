import os
import shutil

from .caches import *

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
from .config import * # pylint: disable=wrong-import-position


if TOKEN == "":
    if TOKEN is None or len(TOKEN) == 0:
        raise Exception(
            "Set 'TOKEN' Environment variable at "
            f"({os.path.join(cur_dir, 'config.py')}) before running bot")
