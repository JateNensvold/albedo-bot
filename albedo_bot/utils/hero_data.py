from enum import Enum
import os
import regex
import json
import yaml

from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, TYPE_CHECKING
from albedo_bot.utils.errors import FileParsingError

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

if TYPE_CHECKING:
    from albedo_bot.bot import AlbedoBot


AsyncCallable = Callable[[Any], Awaitable[Any]]


def translate_afk_helper_path(partial_image_path: str):
    """
    Translate paths from the root of 'afk_helper' repo into the sub module it
        exist under in 'albedo_bot', also resolving all parts of the path that 
        use relative pathing or symlinks

    Args:
        path (str): path to file in 'afk_helper' repo relative to 'afk_helper'
            repo root

    Returns:
        (str): path to file in 'afk_helper' repo relative to 'albedo_bot'
            repo root
    """

    return config.AFK_HELPER_IMAGE_PREFIX.joinpath(
        partial_image_path).resolve()


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
        self.session = session
        new_hero_name: str = hero_dict["name"]

        hero_select = self.db_select(
            Hero).where(Hero.name.ilike(f"{new_hero_name}%"))
        hero_object = await self.db_execute(hero_select).first()

        hero_count = self.count

        hero_faction = hero_dict["faction"]
        hero_class = hero_dict["class"]
        hero_type = hero_dict["type"]
        hero_tier = hero_dict["tier"]

        if hero_object:
            hero_object.hero_faction = hero_faction
            hero_object.hero_class = hero_class
            hero_object.hero_type = hero_type
            hero_object.ascension_tier = hero_tier

            if (hero_object.hero_faction != hero_faction or
                hero_object.hero_class != hero_class or
                hero_object.hero_type != hero_type or
                    hero_object.ascension_tier != hero_tier):
                print(
                    f"Updating Hero #{hero_count} - {new_hero_name} to database")
                await self.db_add(hero_object)
        else:
            print(f"Adding Hero #{hero_count} - {new_hero_name} to database")
            hero_object = Hero(name=new_hero_name,
                               hero_faction=hero_faction,
                               hero_class=hero_class,
                               hero_type=hero_type,
                               ascension_tier=hero_tier)

        await self.db_add(hero_object)
        portrait_path = translate_afk_helper_path(hero_dict["portrait"])

        portrait_select = self.db_select(
            HeroPortrait).where(HeroPortrait.id == hero_object.id,
                                HeroPortrait.image_index == 0,
                                HeroPortrait.required == True)
        portrait_object = await self.db_execute(portrait_select).first()

        if not portrait_object:
            hero_portrait = HeroPortrait(
                id=hero_object.id, image_index=0,
                required=True,
                image_directory=str(portrait_path.parent),
                image_name=portrait_path.name)
            await self.db_add(hero_portrait)

        for skill_dict in hero_dict["skills"]:
            skill_name = skill_dict["name"]

            skill_select = self.db_select(HeroSkill).where(
                HeroSkill.hero_id == hero_object.id,
                HeroSkill.skill_name == skill_name)
            hero_skill = await self.db_execute(skill_select).first()

            if hero_skill:
                hero_skill.description = skill_dict["desc"]
                hero_skill.skill_image = skill_dict["image"]
                hero_skill.skill_type = skill_dict["type"]
                hero_skill.skill_unlock = str(skill_dict["unlock"])
            else:
                hero_skill = HeroSkill(hero_id=hero_object.id,
                                       skill_name=skill_name,
                                       description=skill_dict["desc"],
                                       skill_image=skill_dict["image"],
                                       skill_type=skill_dict["type"],
                                       skill_unlock=str(skill_dict["unlock"]))
            await self.db_add(hero_skill)

            for skill_upgrade_dict in skill_dict["upgrades"]:

                skill_unlock = str(skill_upgrade_dict["unlock"])
                unlock_type = skill_upgrade_dict["type"]
                description = skill_upgrade_dict["desc"]

                skill_upgrade_select = self.db_select(HeroSkillUpgrade).where(
                    HeroSkillUpgrade.skill_id == hero_skill.skill_id,
                    HeroSkillUpgrade.skill_unlock == skill_unlock,
                    HeroSkillUpgrade.unlock_type == unlock_type
                )

                skill_upgrade = await self.db_execute(
                    skill_upgrade_select).first()

                if skill_upgrade:
                    skill_upgrade.description = description
                else:
                    skill_upgrade = HeroSkillUpgrade(
                        skill_id=hero_skill.skill_id,
                        description=description,
                        skill_unlock=skill_unlock,
                        unlock_type=unlock_type)

                await self.db_add(skill_upgrade)

        hero_si_dict = hero_dict["sig_item"]

        hero_si_select = self.db_select(HeroSignatureItem).where(
            HeroSignatureItem.id == hero_object.id)

        hero_si = await self.db_execute(hero_si_select).first()

        si_name = hero_si_dict["name"]
        si_image = hero_si_dict["image"]
        si_description = hero_si_dict["desc"]

        if hero_si:
            hero_si.si_name = si_name
            hero_si.image = si_image
            hero_si.description = si_description
        else:
            hero_si = HeroSignatureItem(id=hero_object.id,
                                        si_name=si_name,
                                        image=si_image,
                                        description=si_description)
        await self.db_add(hero_si)

        for si_upgrade_dict in hero_si_dict["upgrades"]:
            si_upgrade_description = si_upgrade_dict["desc"]
            si_upgrade_level = si_upgrade_dict["unlock"]

            hero_si_upgrade_select = self.db_select(
                HeroSignatureItemUpgrade).where(
                HeroSignatureItemUpgrade.id == hero_object.id,
                HeroSignatureItemUpgrade.si_level == si_upgrade_level)

            hero_si_upgrade = await self.db_execute(
                hero_si_upgrade_select).first()

            if hero_si_upgrade:
                hero_si_upgrade.description = si_upgrade_description
            else:
                hero_si_upgrade = HeroSignatureItemUpgrade(
                    id=hero_object.id,
                    description=si_upgrade_description,
                    si_level=si_upgrade_level)
            await self.db_add(hero_si_upgrade)

        hero_furniture_select = self.db_select(HeroFurniture).where(
            HeroFurniture.id == hero_object.id)
        hero_furniture = await self.db_execute(hero_furniture_select).first()

        hero_furniture_dict = hero_dict["furniture"]
        furniture_name = hero_furniture_dict["name"]
        furniture_image = hero_furniture_dict["image"]

        if hero_furniture:
            hero_furniture.furniture_name = furniture_name
            hero_furniture.image = furniture_image
        else:
            hero_furniture = HeroFurniture(
                id=hero_object.id,
                furniture_name=furniture_name,
                image=furniture_image)
        await self.db_add(hero_furniture)

        for furniture_upgrade_dict in hero_furniture_dict["upgrades"]:

            furniture_upgrade_desc = furniture_upgrade_dict["desc"]
            furniture_upgrade_unlock = furniture_upgrade_dict["unlock"]

            hero_furniture_upgrade_select = self.db_select(
                HeroFurnitureUpgrade).where(
                HeroFurnitureUpgrade.id == hero_object.id,
                (HeroFurnitureUpgrade.furniture_unlock ==
                 furniture_upgrade_unlock))
            hero_furniture_upgrade = await self.db_execute(
                hero_furniture_upgrade_select).first()

            if hero_furniture_upgrade:
                hero_furniture_upgrade.description = furniture_upgrade_desc
            else:
                hero_furniture_upgrade = HeroFurnitureUpgrade(
                    id=hero_object.id,
                    description=furniture_upgrade_desc,
                    furniture_unlock=furniture_upgrade_unlock)
            await self.db_add(hero_furniture_upgrade)


class ParseMethod(Enum):
    """
    An enum class for all the ways that hero_data files can be parsed
    """
    yaml: str = "yaml"
    json: str = "json"


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

    @staticmethod
    def parse_file(bot: "AlbedoBot", file_path: Path,
                   parse_method: ParseMethod = ParseMethod.json):
        """
        Parse the file found at `file_path` for HeroData contents

        Meant to be run on files like the one found at
        https://github.com/Dae314/AFKBuilder/blob/main/src/stores/HeroData.js

        This parsing method is not stable, any changes to the formatting of
        the source file will potentially result in a result that is 
        invalid JSON

        Args:
            bot (AlbedoBot): active discord.py bot
            file_path (Path): path to file
            parse_method (ParseMethod, optional): THe method that should be
                used to parse the file. Defaults to ParseMethod.yaml.

        Raises:
            FileParsingError: When an issue occurs while parsing the file

        Returns:
            dict: a dictionary of hero data
        """
        content_start = "\(\["
        content_end = "\]\)"

        hero_data = {}
        try:
            with file_path.open("r", encoding="utf-8") as file_pointer:
                file_contents = file_pointer.read()

                hero_data_regex_result = regex.search(
                    f"{content_start}(.*){content_end}",
                    file_contents, regex.DOTALL)
                raw_hero_result = hero_data_regex_result.group(1)
                # hero_result = raw_hero_result
                raw_hero_result = f"[\n{raw_hero_result}\n]"

                if parse_method == ParseMethod.json:
                    # Escape double quotes in text to prevent
                    #   early termination
                    double_quote_regex = regex.compile(
                        r'"')
                    raw_hero_result = double_quote_regex.sub(
                        r'\"', raw_hero_result)

                    # Double quote all keys as required by JSON spec
                    # This regex will match a word then a colon that has
                    # 1 whitespace/bracket followed by another whitespace
                    # before the match and 1 whitespace after.
                    # This can result in a false positive in text like the
                    # following "of Esperia: ". There is no easy fix without
                    # using a non-fixed width lookbehind to check for criteria
                    # that text cannot have. Until then we will assume this
                    # edge case will never occur
                    dictionary_key_regex = regex.compile(
                        r"(?<=[\s{]\s)(\w*?)(?=:\s)")
                    raw_hero_result = dictionary_key_regex.sub(
                        r'"\1"', raw_hero_result)

                    # Replace trailing commas as required by JSON spec
                    trailing_comma_bracket_regex = regex.compile(
                        r",(?=\s+\})")
                    raw_hero_result = trailing_comma_bracket_regex.sub(
                        r' ', raw_hero_result)

                    # Replace trailing commas as required by JSON spec
                    trailing_comma_square_bracket_regex = regex.compile(
                        r",(?=\s+\])")
                    raw_hero_result = trailing_comma_square_bracket_regex.sub(
                        r' ', raw_hero_result)

                    hero_data_path = config.JSON_CONFIG_FOLDER_PATH.joinpath(
                        "temp_hero_data.json")
                elif parse_method == ParseMethod.yaml:
                    # Replace all tabs with spaces as yaml does not
                    #   support tabs
                    tab_regex = regex.compile(r"\t")
                    raw_hero_result = tab_regex.sub(
                        r'    ', raw_hero_result)

                    hero_data_path = config.JSON_CONFIG_FOLDER_PATH.joinpath(
                        "temp_hero_data.yaml")

                # Replace leading single quotes as required by
                #   JSON and Yaml spec
                leading_single_quote_regex = regex.compile(r"(?<=\s)'")
                raw_hero_result = leading_single_quote_regex.sub(
                    r'"', raw_hero_result)

                # Replace trailing single quotes as required by
                #   JSON and Yaml spec
                trailing_single_quote_regex = regex.compile(
                    r"(?<!\\)'(?=\s|,)")
                raw_hero_result = trailing_single_quote_regex.sub(
                    r'"', raw_hero_result)

                # Replace escaped single quotes as required by
                #   JSON and YAML spec
                escaped_single_quote_regex = regex.compile(r"\\'")
                raw_hero_result = escaped_single_quote_regex.sub(
                    r"'", raw_hero_result)

                # Escape all backslash(\) that are not associated with a
                #   double quote("") are escaped
                backslash_regex = regex.compile(r'\\(?!\")')
                hero_result = backslash_regex.sub(
                    r'\\\\', raw_hero_result)

                # hero_result = raw_hero_result

                if parse_method == parse_method.json:
                    hero_data = json.loads(hero_result)
                elif parse_method == ParseMethod.yaml:
                    hero_data = yaml.safe_load(hero_result)

        except Exception as exception:
            with hero_data_path.open("w",
                                     encoding="utf-8") as file_pointer:
                file_pointer.write(hero_result)

            raise FileParsingError(
                (f"Unable to parse file `{file_path}`. Invalid contents have "
                 f"been written to `{hero_data_path}`. This could be due to a "
                 f"file formatting or API change, contact {bot.owner_string} "
                 "for further investigation.")) from exception
        return hero_data

    async def build(self, session: AsyncSession, portrait_folders: list[Path]):
        """
        Build all the heroes stored in self.hero_data and add them to the
            database using `session`

        Args:
            session (AsyncSession): session connection to databases
            portrait_folders (list[Path]): a list of paths to folders 
                containing HeroPortraits
        """
        self.session = session
        for hero_dict in self.hero_data:
            json_hero = JsonHero(hero_dict)
            await json_hero.build(session)

        await self._add_portraits(portrait_folders)
        self.session = None

    async def _add_portraits(self, portrait_folders: list[Path]):
        """
        Find and parse all the HeroPortrait that are located in
            `portrait_folder`

        Args:
            portrait_folders (list[Path]): a list of paths to folders 
                containing HeroPortraits
        """
        for portrait_folder in portrait_folders:
            print(f"Adding portraits from {portrait_folder}")
            portrait_path_list = os.listdir(portrait_folder)
            for portrait_name in portrait_path_list:
                portrait_path = Path(portrait_folder, portrait_name)
                if os.path.isdir(portrait_path):
                    continue
                name_info = PortraitNameInfo.from_str(portrait_name)

                hero_object = await Hero.ilike(self.session,
                                               name_info.hero_name,
                                               config.hero_alias).first()

                if hero_object:
                    hero_portrait_select = self.db_select(HeroPortrait).where(
                        HeroPortrait.id == hero_object.id,
                        HeroPortrait.image_index == name_info.image_index,
                        HeroPortrait.required == name_info.required)
                    hero_portrait = await self.db_execute(
                        hero_portrait_select).first()

                    if not hero_portrait:
                        print(f"Adding portrait {portrait_path}")
                        hero_portrait = HeroPortrait(
                            id=hero_object.id,
                            image_index=name_info.image_index,
                            required=name_info.required,
                            image_directory=str(portrait_folder),
                            image_name=portrait_name)
                        await self.db_add(hero_portrait)
                else:
                    print(f"Skipping image: '{portrait_name}', "
                          "unable to find a hero that matches")
