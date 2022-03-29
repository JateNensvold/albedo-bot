import argparse
import os
import json
from typing import Dict

from discord.ext import commands
from sqlalchemy.orm import Session

from albedo_bot.database.database import Database

par_dir = os.path.dirname(__file__)

CONFIG_FOLDER_PATH = os.path.join(par_dir, "config")

PERMISSIONS_JSON_PATH = os.path.join(
    CONFIG_FOLDER_PATH, "permissions_config.json")
DATABASE_JSON_PATH = os.path.join(CONFIG_FOLDER_PATH, "database_config.json")
HERO_JSON_PATH = os.path.join(CONFIG_FOLDER_PATH, "hero_data.json")
GUILD_JSON_PATH = os.path.join(CONFIG_FOLDER_PATH, "guild_config.json")
HERO_ALIAS_JSON_PATH = os.path.join(CONFIG_FOLDER_PATH, "hero_alias.json")
AFK_HELPER_PATH = os.path.join(par_dir, "albedo_bot", "afk_helper")

AFK_HELPER_IMAGE_PREFIX = "../afk_helper"

with open(HERO_ALIAS_JSON_PATH, "r", encoding="utf-8") as file:
    _alias_data = json.load(file)
    HERO_ALIAS: Dict[str, str] = _alias_data["alias"]


def translate_afk_helper_path(path: str):
    """
    Translate paths from the root of 'afk_helper' repo into the sub module it
        exist under in 'albedo_bot'

    Args:
        path (str): path to file in 'afk_helper' repo relative to 'afk_helper' 
            repo root

    Returns:
        (str): path to file in 'afk_helper' repo relative to 'albedo_bot'
            repo root
    """
    striped_path = os.path.relpath(path, AFK_HELPER_IMAGE_PREFIX)
    return os.path.join(AFK_HELPER_PATH, striped_path)


PERMISSIONS_DATA: Dict = None
DATABASE_DATA: Dict = None
DATABASE: Database = None
# When using a global session object import his module as
#   `import albedo_bot.global_values as GV` and access the session object as
#   GV.session. This allows for dynamic updates to the session object when a
#   new database connection is created. When importing a python object from a
#   module as from albedo_bot.global_values import session, the object is only
#   import once on file initialization and the import module is not placed in a
#   shared module space
session: Session = None


def update_session(new_session: Session):
    """_summary_

    Args:
        new_session (Session): _description_
    """
    global session  # pylint: disable=global-statement, invalid-name
    session = new_session


with open(DATABASE_JSON_PATH, "r", encoding="utf-8") as file:
    DATABASE_DATA = json.load(file)
    DATABASE = Database(DATABASE_DATA["user"], DATABASE_DATA["password"],
                        DATABASE_DATA["address"], session_callback=update_session)
bot = commands.Bot(command_prefix="%")


def setup(bot_client: commands.Bot):
    """_summary_

    Args:
        bot (commands.Bot): _description_
    """
    bot_client.add_cog(ErrorHandler(bot_client))

@bot.event
async def on_command_error(ctx: commands.Context, error: Exception):
    """A global error handler cog."""
    message = "".join(error.args)
    print(message)
    await ctx.send(message)
    # if isinstance(error, (DiscordPermissionError, commands.BadArgument)):
    #     return
    raise error


# Load ErrorHandler after bot to prevent circular import
from albedo_bot.commands.helpers.errors import ErrorHandler  # noqa pylint: disable=wrong-import-position

# Load permissions after initializing database and bot to prevent circular
# import
from albedo_bot.commands.helpers.permissions import Permissions  # noqa pylint: disable=wrong-import-position

with open(PERMISSIONS_JSON_PATH, "r", encoding="utf-8") as file:
    PERMISSIONS_DATA = json.load(file)
    for role_name, role_data in PERMISSIONS_DATA.items():
        Permissions(role_name, role_data["names"],
                    role_data["roles"], role_data["priority"])


parser = argparse.ArgumentParser(description='AFK arena object extraction and '
                                 'image analysis.')

parser.add_argument("-v", "--verbose", help="Increase verbosity of output"
                    "from discord commands", action='count', default=0)

args = parser.parse_args()

VERBOSE = args.verbose