# pylint: disable-all
import os
import shutil

from .caches import *

cur_dir = os.path.abspath(os.path.dirname(__file__))
if "config.py" not in os.listdir(cur_dir):
    shutil.copyfile(os.path.join(cur_dir, "default_config.py"),
                    os.path.join(cur_dir, "config.py"))
# autopep8: off
from .config import *

from .json_config import (
    permissions, database_config, database, prefixes, blacklist, hero_alias)
from .json_config import (
    AFK_HELPER_PATH, AFK_HELPER_IMAGE_PREFIX, BLACKLIST_JSON_PATH,
    CONFIG_FOLDER_PATH, DATABASE_CONFIG_JSON_PATH, GUILD_JSON_PATH,
    HERO_ALIAS_JSON_PATH, HERO_JSON_PATH, PERMISSIONS_JSON_PATH,
    PREFIX_JSON_PATH)

def check_value(value:str, value_name:str):
    """
    Check if a value in the config.py file has been initialized 

    Args:
        value (str): value to check
    """
    if value == "":
        if value is None or len(value) == 0:
            raise Exception(
                f"Set '{value_name}' Environment variable at "
                f"({os.path.join(cur_dir, 'config.py')}) before running bot")


check_value(TOKEN, "TOKEN")
check_value(DATABASE_PASS, "DATABASE_PASS")
check_value(DATABASE_USER, "DATABASE_USER")
