import os
from pathlib import Path
import re
from typing import Any, Awaitable, Callable, Dict, List

from sqlalchemy.ext.asyncio import AsyncSession
import image_processing.globals as GV

from albedo_bot.cogs.utils.mixins.database_mixin import DatabaseMixin
from albedo_bot.database.schema.hero import (Hero)
from albedo_bot.database.schema.hero.hero_portrait import HeroPortrait, PortraitNameInfo
from albedo_bot.database.schema.hero.hero_si import (HeroSignatureItem,
                                                     HeroSignatureItemUpgrade)
from albedo_bot.database.schema.hero.hero_skill import (
    HeroSkill, HeroSkillUpgrade)
from albedo_bot.database.schema.hero.hero_furniture import (
    HeroFurniture, HeroFurnitureUpgrade)
from albedo_bot.utils.config import Config

import albedo_bot.config as config

AsyncCallable = Callable[[Any], Awaitable[Any]]


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

    return config.AFK_HELPER_IMAGE_PREFIX.joinpath(path)


class JsonHero(DatabaseMixin):
    """
    A json representation of a hero
    """
    _count = 0

    def __init__(self, hero_dict: Dict[str, Any]):
        """
        Create a json hero from a dictionary and accept a session_callback so
        the hero can be added to a hero database when `build` is called

        Args:
            hero_dict (Dict[str, Any]): dictionary representing the heroes data
        """

        self.hero_dict = hero_dict

    @classmethod
    @property
    def count(cls):
        """
        A way to track all the times that a hero has been created each session

        Returns:
            int: number of times count has been called this session
        """
        cls._count += 1
        return cls._count

    async def build(self, session: AsyncSession):
        """
        Build the JsonHero with all its components in the database
        """
        hero_dict = self.hero_dict

        print(f"Adding Hero #{self.count} - {hero_dict['name']} to database")
        new_hero = Hero(name=hero_dict["name"],
                        hero_faction=hero_dict["faction"],
                        hero_class=hero_dict["class"],
                        hero_type=hero_dict["type"],
                        ascension_tier=hero_dict["tier"],
                        hero_portrait=translate_afk_helper_path(
                        hero_dict["portrait"]))

        portrait_path = translate_afk_helper_path(hero_dict["portrait"])
        await self.db_add(new_hero)

        hero_portrait = HeroPortrait(id=new_hero.id, image_index=0,
                                     required=True,
                                     image_directory=portrait_path.parent,
                                     image_name=portrait_path.name)
        await self.db_add(hero_portrait)

        for skill_dict in hero_dict["skills"]:

            skill_name = skill_dict["name"]
            hero_skill = HeroSkill(hero_id=new_hero.id,
                                   skill_name=skill_name,
                                   description=skill_dict["desc"],
                                   skill_image=skill_dict["image"],
                                   skill_type=skill_dict["type"],
                                   skill_unlock=str(skill_dict["unlock"]))
            await self.db_add(hero_skill)

            for skill_upgrade_dict in skill_dict["upgrades"]:
                skill_upgrade = HeroSkillUpgrade(
                    skill_id=hero_skill.skill_id,
                    description=skill_upgrade_dict["desc"],
                    skill_unlock=str(skill_upgrade_dict["unlock"]),
                    unlock_type=skill_upgrade_dict["type"])

                await self.db_add(skill_upgrade, update=False)

        hero_si_dict = hero_dict["sig_item"]

        hero_si = HeroSignatureItem(id=new_hero.id,
                                    si_name=hero_si_dict["name"],
                                    image=hero_si_dict["image"],
                                    description=hero_si_dict["desc"])
        await self.db_add(hero_si)
        for si_upgrade_dict in hero_si_dict["upgrades"]:
            hero_si_upgrade = HeroSignatureItemUpgrade(
                id=new_hero.id,
                description=si_upgrade_dict["desc"],
                si_level=si_upgrade_dict["unlock"])
            await self.db_add(hero_si_upgrade)

        hero_furniture_dict = hero_dict["furniture"]
        hero_furniture = HeroFurniture(
            id=new_hero.id,
            furniture_name=hero_furniture_dict["name"],
            image=hero_furniture_dict["image"])
        await self.db_add(hero_furniture)
        for furniture_upgrade_dict in hero_furniture_dict["upgrades"]:
            furniture_upgrade = HeroFurnitureUpgrade(
                id=new_hero.id,
                description=furniture_upgrade_dict["desc"],
                furniture_unlock=furniture_upgrade_dict["unlock"])
            await self.db_add(furniture_upgrade)


class HeroData(Config, DatabaseMixin):
    """
    A wrapper around the json Representation of a Hero
    """

    def __init__(self, file_path: Path):
        """
        Create HeroData from a list of dictionaries

        Args:
            hero_data (List[Dict[str, Any]]): json hero data
        """
        super().__init__(file_path)

        self.hero_data: List[Dict[str, Any]] = self._db

    async def build(self, session: AsyncSession, portrait_folder: Path):
        """
        Build all the heroes stored in self.hero_data and add them to the
            database using `session`

        Args:
            session (AsyncSession): session connection to databases
        """
        self.session = session
        for hero_dict in self.hero_data:
            json_hero = JsonHero(hero_dict)
            await json_hero.build(session)

        self._add_portraits(portrait_folder)
        self.session = None

    async def _add_portraits(self, portrait_folder: Path):
        """
        Find and parse all the HeroPortrait that are located in
            `portrait_folder`

        Args:
            portrait_folder (Path): path to folder containing HeroPortraits
        """
        portrait_path_list = os.listdir(portrait_folder)

        for portrait_name in portrait_path_list:

            name_info = PortraitNameInfo.from_str(portrait_name)

            hero_select = self.db_select(
                Hero).where(Hero.name.ilike(f"{name_info.hero_name}%"))
            hero_object = await self.db_execute(hero_select).first()

            hero_portrait = HeroPortrait(id=hero_object.id,
                                         image_index=name_info.image_index,
                                         required=name_info.required,
                                         image_directory=str(portrait_folder),
                                         image_name=name_info.hero_name)

            await self.db_add(hero_portrait)
