import json
from typing import Dict, List, Union

from sqlalchemy.orm import Session

# Import schema files so create_all creates all tables
import albedo_bot.schema  # pylint: disable=unused-import
from albedo_bot.schema import Hero
import albedo_bot.global_values as GV
from albedo_bot.database.database import Database


def load_hero_json(file_path: str, database: Database):
    """[summary]

    Args:
        file_path (str): path to json containing information about hero skills
    """
    session = Session(bind=database.engine, autoflush=True, autocommit=True)

    with open(file_path, "r", encoding="utf-8") as file:
        hero_data = json.load(file)
        # print(hero_data)
        # print(type(hero_data))
        for hero in hero_data:
            print(type(hero), hero.keys(), hero["name"])
            add_hero(hero, session)


def add_hero(hero_dict: Dict[str, Union[str, List]], session: Session):
    """[summary]

    Args:
        hero_dict (Dict[str, Union[str, List]]): [description]
        session (Session): [description]
    """
    new_hero = Hero(name=hero_dict["name"])
    session.add(new_hero)
    session.flush()


def main():
    """[summary]
    """

    afk_database = GV.DATABASE
    afk_database.create_database(GV.DATABASE_DATA["name"], raise_error=False)
    afk_database.create_tables()
    print(afk_database.engine.url)
    print(afk_database.list_tables())
    load_hero_json(GV.HERO_JSON_PATH, afk_database)


if __name__ == "__main__":
    main()
