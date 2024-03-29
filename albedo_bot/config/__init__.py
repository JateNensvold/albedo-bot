# pylint: disable-all
import os
import shutil

from .cache_config import *

cur_dir = os.path.abspath(os.path.dirname(__file__))


def copy_default(original_path: str, new_path: str):
    """
    Copy a file from one location to another under a new name

    Args:
        original_path (str): path to original file
        new_path (str): path to where new file will exist
    """
    if not os.path.exists(new_path):
        shutil.copyfile(original_path, new_path)


# Generate the config.py from the default
copy_default(os.path.join(cur_dir, "default_config.py"),
             os.path.join(cur_dir, "config.py"))

# autopep8: off
from .config import *

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


# Import json_paths in json_configs before json_config so they can use the
#   paths to initialize the json based classes
from .json_configs import *

database_config_dir = DATABASE_CONFIG_JSON_PATH.parent
database_config_name = DATABASE_CONFIG_JSON_PATH.name
# Generate the database_config from the default
copy_default(
    database_config_dir.joinpath(f"default_{database_config_name}"),
    DATABASE_CONFIG_JSON_PATH)

from albedo_bot.config.config_objects import ConfigObjects
# Import module as object to allow the following objects to be used
#   as singletons

_config_objects = ConfigObjects()

permissions = _config_objects.permissions
# database_config = _config_objects.database_config
# prefixes = _config_objects.prefixes
# blacklist = _config_objects.blacklist
# hero_alias = _config_objects.hero_alias
# hero_data = _config_objects.hero_data
processing_client = _config_objects.processing_client
reload_loop = _config_objects.reload_loop
# database = _config_objects.database
# get_database = config_objects.get_database
# config_objects.get_hero_data = config_objects.get_hero_data
objects = _config_objects