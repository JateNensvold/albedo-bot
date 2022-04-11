
import os
import shutil
cur_dir = os.path.abspath(os.path.dirname(__file__))
if "config.py" not in os.listdir(cur_dir):
    shutil.copyfile(os.path.join(cur_dir, "default_config.py"),
                    os.path.join(cur_dir, "config.py"))
# autopep8: off
from .json_config import (
    permissions, database, prefixes, blacklist)
from .config import token, database_name, VERBOSE # pylint: disable=wrong-import-position

if token == "":
    if token is None or len(token) == 0:
        raise Exception(
            "Set 'token' Environment variable at "
            f"({os.path.join(cur_dir, 'config.py')}) before running bot")
