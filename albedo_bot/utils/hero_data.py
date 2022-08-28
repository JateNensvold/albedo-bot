
import json
from typing import Any, Callable, Dict, List

from albedo_bot.database.schema.hero import (Hero)

from albedo_bot.database.schema.hero.hero_si import (HeroSignatureItem,
                                                     HeroSignatureItemUpgrade)

from albedo_bot.database.schema.hero.hero_skill import (
    HeroSkill, HeroSkillUpgrade)

from albedo_bot.database.schema.hero.hero_furniture import (
    HeroFurniture, HeroFurnitureUpgrade)

import albedo_bot.config as config


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

    return str(config.AFK_HELPER_IMAGE_PREFIX.joinpath(path))


class JsonHero:
    """_summary_
    """
    _count = 0

    def __init__(self, hero_dict: Dict[str, Any], session_callback: Callable):
        """_summary_

        Args:
            hero_dict (Dict[str, Any]): _description_

        Returns:
            _type_: _description_
        """

        self.hero_dict = hero_dict
        self.session_callback = session_callback

    @classmethod
    @property
    def count(cls):
        """_summary_

        Returns:
            _type_: _description_
        """
        cls._count += 1
        return cls._count

    async def build(self):
        """_summary_
        """
        session_callback = self.session_callback
        hero_dict = self.hero_dict

        print(f"Adding Hero #{self.count} - {hero_dict['name']} to database")
        new_hero = Hero(name=hero_dict["name"],
                        hero_faction=hero_dict["faction"],
                        hero_class=hero_dict["class"],
                        hero_type=hero_dict["type"],
                        ascension_tier=hero_dict["tier"],
                        hero_portrait=translate_afk_helper_path(
                        hero_dict["portrait"]))
        await session_callback(new_hero)
        for skill_dict in hero_dict["skills"]:

            skill_name = skill_dict["name"]
            hero_skill = HeroSkill(hero_id=new_hero.id,
                                   skill_name=skill_name,
                                   description=skill_dict["desc"],
                                   skill_image=skill_dict["image"],
                                   skill_type=skill_dict["type"],
                                   skill_unlock=str(skill_dict["unlock"]))
            await session_callback(hero_skill)

            for skill_upgrade_dict in skill_dict["upgrades"]:
                skill_upgrade = HeroSkillUpgrade(
                    skill_id=hero_skill.skill_id,
                    description=skill_upgrade_dict["desc"],
                    skill_unlock=str(skill_upgrade_dict["unlock"]),
                    unlock_type=skill_upgrade_dict["type"])

                await session_callback(skill_upgrade, update=False)

        hero_si_dict = hero_dict["sig_item"]

        hero_si = HeroSignatureItem(id=new_hero.id,
                                    si_name=hero_si_dict["name"],
                                    image=hero_si_dict["image"],
                                    description=hero_si_dict["desc"])
        await session_callback(hero_si)
        for si_upgrade_dict in hero_si_dict["upgrades"]:
            hero_si_upgrade = HeroSignatureItemUpgrade(
                id=new_hero.id,
                description=si_upgrade_dict["desc"],
                si_level=si_upgrade_dict["unlock"])
            await session_callback(hero_si_upgrade)

        hero_furniture_dict = hero_dict["furniture"]
        hero_furniture = HeroFurniture(
            id=new_hero.id,
            furniture_name=hero_furniture_dict["name"],
            image=hero_furniture_dict["image"])
        await session_callback(hero_furniture)
        for furniture_upgrade_dict in hero_furniture_dict["upgrades"]:
            furniture_upgrade = HeroFurnitureUpgrade(
                id=new_hero.id,
                description=furniture_upgrade_dict["desc"],
                furniture_unlock=furniture_upgrade_dict["unlock"])
            await session_callback(furniture_upgrade)


class HeroData:
    """_summary_
    """

    def __init__(self, hero_data: List[Dict[str, Any]],
                 session_callback: Callable):
        """_summary_

        Args:
            hero_data (List[Dict[str, Any]]): _description_
            session_callback (Callable): _description_
        """
        self.hero_data = hero_data
        self.session_callback = session_callback

    async def build(self):
        """_summary_
        """
        for hero_dict in self.hero_data:
            json_hero = JsonHero(hero_dict, self.session_callback)
            await json_hero.build()

    @classmethod
    def from_json(cls, json_path: str, session_callback: Callable):
        """[summary]

        Args:
            file_path (str): path to json containing information about
                hero skills
        """
        with open(json_path, "r", encoding="utf-8") as file:
            hero_data = json.load(file)

        return HeroData(hero_data, session_callback)
