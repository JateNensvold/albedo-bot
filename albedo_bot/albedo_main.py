import os
import json
from typing import Dict
from sqlalchemy.orm import Session

# Import commands so bot will register all commands
import albedo_bot.commands  # pylint: disable=unused-import
from albedo_bot.global_values import bot
import albedo_bot.global_values as GV

TOKEN = os.getenv('TOKEN')
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
CONFIG_DATA: Dict = None


class ConfigData:
    """[summary]
    """

    def __init__(self, file_path: str, skip_file: bool = False):
        """[summary]

        Args:
            file_path (str): [description]
        """
        if skip_file:
            return
        self.data = {}
        self.read_config(file_path)
        self.file_path = file_path

    def read_config(self, config_path: str):
        """[summary]
        """

        with open(config_path, "r", encoding="utf-8") as file:
            self.data = json.load(file)

    def write_config(self):
        """[summary]
        """
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(self.data, file)

    def __enter__(self):
        """
        """

        return self

    def __exit__(self,  _exc_type, _exc_value, _traceback):
        """[summary]
        """
        GV.session.flush()


def main():
    """[summary]
    """

    with ConfigData(GV.GUILD_JSON_PATH, skip_file=True) as data:
        global CONFIG_DATA  # pylint: disable=global-statement
        CONFIG_DATA = data

        GV.DATABASE.postgres_connect(GV.DATABASE_DATA["user"],
                                     GV.DATABASE_DATA["password"],
                                     GV.DATABASE_DATA["address"],
                                     GV.DATABASE_DATA["name"])
        if TOKEN is None:
            raise Exception(
                "Set 'TOKEN' Environment variable before running bot")
        print(f"Database tables: {GV.DATABASE.list_tables()}")
        GV.session = Session(bind=GV.DATABASE.engine, autoflush=True, autocommit=True)

        bot.run(TOKEN)


if __name__ == "__main__":
    main()
