import json
from typing import Any, Dict, List, Union

from sqlalchemy.orm import Session

# Import schema files so create_all creates all tables
import albedo_bot.schema  # pylint: disable=unused-import
from albedo_bot.schema import (
    Hero, HeroSkill, HeroSkillUpgrade, HeroSignatureItem,
    HeroSignatureItemUpgrade, HeroFurniture, HeroFurnitureUpgrade)
import albedo_bot.global_values as GV
from albedo_bot.database.database import Database


def add_and_update(session: Session, sql_object: Any) -> Any:
    """_summary_

    Args:
        session (Session): _description_
        object (Any): _description_

    Returns:
        Any: _description_
    """
    session.add(sql_object)
    session.flush()
    session.refresh(sql_object)


def load_hero_json(file_path: str, database: Database):
    """[summary]

    Args:
        file_path (str): path to json containing information about hero skills
    """
    session = Session(bind=database.engine, autoflush=True, autocommit=True)

    with open(file_path, "r", encoding="utf-8") as file:
        hero_data = json.load(file)

        for hero in hero_data:
            add_hero(hero, session)


def add_hero(hero_dict: Dict[str, Union[str, List]], session: Session):
    """[summary]

    Args:
        hero_dict (Dict[str, Union[str, List]]): [description]
        session (Session): [description]
    """
    new_hero = Hero(name=hero_dict["name"],
                    hero_faction=hero_dict["faction"],
                    hero_class=hero_dict["class"],
                    hero_type=hero_dict["type"],
                    ascension_tier=hero_dict["tier"],
                    hero_portrait=hero_dict["portrait"])
    add_and_update(session, new_hero)
    print(new_hero)

    for skill_dict in hero_dict["skills"]:

        skill_name = skill_dict["name"]
        hero_skill = HeroSkill(hero_id=new_hero.id,
                               skill_name=skill_name,
                               description=skill_dict["desc"],
                               skill_image=skill_dict["image"],
                               skill_type=skill_dict["type"],
                               skill_unlock=skill_dict["unlock"])
        add_and_update(session, hero_skill)

        for skill_upgrade_dict in skill_dict["upgrades"]:
            skill_upgrade = HeroSkillUpgrade(skill_id=hero_skill.skill_id,
                                             description=skill_upgrade_dict["desc"],
                                             skill_unlock=skill_upgrade_dict["unlock"],
                                             unlock_type=skill_upgrade_dict["type"])
            session.add(skill_upgrade)
    hero_si_dict = hero_dict["sig_item"]

    hero_si = HeroSignatureItem(id=new_hero.id,
                                si_name=hero_si_dict["name"],
                                image=hero_si_dict["image"],
                                description=hero_si_dict["desc"])
    session.add(hero_si)
    for si_upgrade_dict in hero_si_dict["upgrades"]:
        hero_si_upgrade = HeroSignatureItemUpgrade(
            id=new_hero.id,
            description=si_upgrade_dict["desc"],
            si_level=si_upgrade_dict["unlock"])
        session.add(hero_si_upgrade)

    hero_furniture_dict = hero_dict["furniture"]
    hero_furniture = HeroFurniture(id=new_hero.id,
                                   furniture_name=hero_furniture_dict["name"],
                                   image=hero_furniture_dict["image"])
    session.add(hero_furniture)
    for furniture_upgrade_dict in hero_furniture_dict["upgrades"]:
        furniture_upgrade = HeroFurnitureUpgrade(
            id=new_hero.id,
            description=furniture_upgrade_dict["desc"],
            furniture_unlock=furniture_upgrade_dict["unlock"])
        session.add(furniture_upgrade)
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
