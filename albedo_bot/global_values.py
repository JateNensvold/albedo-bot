from albedo_bot.commands.helpers.permissions import Permissions
import os
import json
from typing import Dict

from discord.ext import commands
from sqlalchemy.orm import Session
from albedo_bot.database.database import Database
from albedo_bot.commands.helpers.errors import ErrorHandler
par_dir = os.path.dirname(__file__)

CONFIG_FOLDER_PATH = os.path.join(par_dir, "config")

PERMISSIONS_JSON_PATH = os.path.join(
    CONFIG_FOLDER_PATH, "permissions_config.json")
DATABASE_JSON_PATH = os.path.join(CONFIG_FOLDER_PATH, "database_config.json")
HERO_JSON_PATH = os.path.join(CONFIG_FOLDER_PATH, "heroSkills.json")
GUILD_JSON_PATH = os.path.join(CONFIG_FOLDER_PATH, "guild_config.json")


PERMISSIONS_DATA: Dict = None
DATABASE_DATA: Dict = None
DATABASE: Database = None
# When using a global session object import his module as
#   `import albedo_bot.global_values as GV` and access the session object as
#   GV.session. This allows for dynamic updates to the session object when a
#   new database connection is created. When importing a python object from a
#   module as from albedo_bot.global_values import session, the object is only
#   import once on file initialization and the import module is not place in a
#   shared module space
session: Session = None


def update_session(new_session: Session):
    """_summary_

    Args:
        new_session (Session): _description_
    """
    global session  # pylint: disable=global-statement
    session = new_session


def setup(bot_client: commands.Bot):
    """_summary_

    Args:
        bot (commands.Bot): _description_
    """
    bot_client.add_cog(ErrorHandler(bot_client))


with open(DATABASE_JSON_PATH, "r", encoding="utf-8") as file:
    DATABASE_DATA = json.load(file)
    DATABASE = Database(DATABASE_DATA["user"], DATABASE_DATA["password"],
                        DATABASE_DATA["address"], session_callback=update_session)
bot = commands.Bot(command_prefix="-")
setup(bot)
admin = commands.Bot(command_prefix="--")
setup(admin)

# Load permissions after initializing database to prevent circular import

with open(PERMISSIONS_JSON_PATH, "r", encoding="utf-8") as file:
    PERMISSIONS_DATA = json.load(file)
    for role_name, role_data in PERMISSIONS_DATA.items():
        Permissions(role_name, role_data["names"],
                    role_data["roles"], role_data["priority"])
