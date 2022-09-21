import os
import regex
import json
import yaml
from enum import Enum

from pathlib import Path
from typing import Any, Awaitable, Callable, TYPE_CHECKING
from sqlalchemy.ext.asyncio import AsyncSession

import albedo_bot.config as config
from albedo_bot.utils.errors import FileParsingError
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
from albedo_bot.utils.enums.ascension_type_enum import HeroAscensionEnum
from albedo_bot.utils.enums.hero_class_enum import HeroClassEnum
from albedo_bot.utils.enums.hero_faction_enum import HeroFactionEnum
from albedo_bot.utils.enums.hero_type_enum import HeroTypeEnum
from albedo_bot.utils.enums.skill_unlock_type_enum import HeroSkillUnlockTypeEnum

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


class JsonHeroFurniture:
    """
    A json representation of a Heroes Furniture
    """

    def __init__(self, furniture_dict: dict[str, Any]) -> None:
        """
        Create a JsonHeroFurniture from a dictionary
        """

        self.furniture_dict = furniture_dict
        self.furniture_name: str = furniture_dict["name"]
        self.furniture_image_path = translate_afk_helper_path(
            furniture_dict["image"])
        self.furniture_upgrades = furniture_dict["upgrades"]


class JsonHeroSignatureItem:
    """
    A json representation of a Heroes Signature Item
    """

    def __init__(self, hero_si_dict: dict[str, Any]):
        """
        Create a JsonHeroSignatureItem from a dictionary
        """
        self.signature_item_dict = hero_si_dict
        self.signature_item_name: str = hero_si_dict["name"]
        self.signature_item_image_path = translate_afk_helper_path(
            hero_si_dict["image"])
        self.signature_item_description: str = hero_si_dict["desc"]
        self.signature_item_upgrades: dict[str, Any] = hero_si_dict["upgrades"]


class JsonHeroSkill(DatabaseMixin):
    """
    A json representation of a Heroes Skills
    """

    def __init__(self, hero_skill: dict[str, Any]):
        """
        Create a JsonHeroSkill from a dictionary
        """

        self.skill_dict = hero_skill
        self.skill_name: str = hero_skill["name"]
        self.skill_description: str = hero_skill["desc"]
        self.skill_image_path = translate_afk_helper_path(hero_skill["image"])
        self.skill_type = HeroSkillUnlockTypeEnum(hero_skill["type"])
        self.skill_unlock = str(hero_skill["unlock"])
        self.skill_upgrades: dict[str, Any] = hero_skill["upgrades"]


class JsonHero(DatabaseMixin):
    """
    A json representation of a hero
    """
    _count = 0

    def __init__(self, hero_dict: dict[str, Any]):
        """
        Create a json hero from a dictionary and accept a session_callback so
        the hero can be added to a hero database when `build` is called

        Args:
            hero_dict (dict[str, Any]): dictionary representing the heroes data
        """

        self.hero_dict = hero_dict
        self.hero_id: str = hero_dict["id"]
        self.hero_name: str = hero_dict["name"]

        self.hero_faction = HeroFactionEnum(hero_dict["faction"])
        self.hero_class = HeroClassEnum(hero_dict["class"])
        self.hero_type = HeroTypeEnum(hero_dict["type"])
        self.hero_tier = HeroAscensionEnum(hero_dict["tier"])
        self.hero_portrait_path: str = hero_dict["portrait"]
        self.hero_skills = [JsonHeroSkill(hero_skill)
                            for hero_skill in hero_dict["skills"]]

        self.signature_item = JsonHeroSignatureItem(hero_dict["sig_item"])
        self.furniture = JsonHeroFurniture(hero_dict["furniture"])

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
        Build the `JsonHero` with all its components in the database

        Args:
            session (AsyncSession): session connection to databases
        Returns:
            Hero: the `Hero` that is associated with this JsonHero
        """
        self.session = session

        hero_select = self.db_select(
            Hero).where(Hero.name.ilike(f"{self.hero_name}%"))
        hero_object = await self.db_execute(hero_select).first()

        # Increment the class count
        hero_count = self.count

        if hero_object:
            hero_object.hero_faction = self.hero_faction.value
            hero_object.hero_class = self.hero_class.value
            hero_object.hero_type = self.hero_type.value
            hero_object.ascension_tier = self.hero_tier.value

            if (hero_object.hero_faction != self.hero_faction.value or
                hero_object.hero_class != self.hero_class.value or
                hero_object.hero_type != self.hero_type.value or
                    hero_object.ascension_tier != self.hero_tier.value):
                print((f"Updating Hero #{hero_count} - "
                       f"{self.hero_name} to database"))
                await self.db_add(hero_object)
        else:
            print(f"Adding Hero #{hero_count} - {self.hero_name} to database")
            hero_object = Hero(name=self.hero_name,
                               hero_faction=self.hero_faction.value,
                               hero_class=self.hero_class.value,
                               hero_type=self.hero_type.value,
                               ascension_tier=self.hero_tier.value)

        await self.db_add(hero_object)
        portrait_path = translate_afk_helper_path(self.hero_portrait_path)

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

        for json_hero_skill in self.hero_skills:

            skill_select = self.db_select(HeroSkill).where(
                HeroSkill.hero_id == hero_object.id,
                HeroSkill.skill_name == json_hero_skill.skill_name)
            hero_skill = await self.db_execute(skill_select).first()

            if hero_skill:
                hero_skill.description = json_hero_skill.skill_description
                hero_skill.skill_image = str(json_hero_skill.skill_image_path)
                hero_skill.skill_type = json_hero_skill.skill_type.value
                hero_skill.skill_unlock = json_hero_skill.skill_unlock
            else:
                hero_skill = HeroSkill(
                    hero_id=hero_object.id,
                    skill_name=json_hero_skill.skill_name,
                    description=json_hero_skill.skill_description,
                    skill_image=str(json_hero_skill.skill_image_path),
                    skill_type=json_hero_skill.skill_type.value,
                    skill_unlock=json_hero_skill.skill_unlock)
            await self.db_add(hero_skill)

            for skill_upgrade_dict in json_hero_skill.skill_upgrades:

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

        hero_si_select = self.db_select(HeroSignatureItem).where(
            HeroSignatureItem.id == hero_object.id)

        hero_si = await self.db_execute(hero_si_select).first()

        if hero_si:
            hero_si.si_name = self.signature_item.signature_item_name
            hero_si.image = str(self.signature_item.signature_item_image_path)
            hero_si.description = self.signature_item.signature_item_description
        else:
            hero_si = HeroSignatureItem(
                id=hero_object.id,
                si_name=self.signature_item.signature_item_name,
                image=str(self.signature_item.signature_item_image_path),
                description=self.signature_item.signature_item_description)
        await self.db_add(hero_si)

        for si_upgrade_dict in self.signature_item.signature_item_upgrades:
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

        if hero_furniture:
            hero_furniture.furniture_name = self.furniture.furniture_name
            hero_furniture.image = str(self.furniture.furniture_image_path)
        else:
            hero_furniture = HeroFurniture(
                id=hero_object.id,
                furniture_name=self.furniture.furniture_name,
                image=str(self.furniture.furniture_image_path))
        await self.db_add(hero_furniture)

        for furniture_upgrade_dict in self.furniture.furniture_upgrades:
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
        return hero_object


class ParseMethod(Enum):
    """
    An enum class for all the ways that hero_data files can be parsed
    """
    yaml: str = "yaml"
    json: str = "json"


HeroDataType = list[dict[str, Any]]


class HeroData(Config, DatabaseMixin):
    """
    A wrapper around the json Representation of a Hero
    """

    def __init__(self, file_path: Path, **kwargs):
        """
        Create HeroData from a list of dictionaries

        Args:
            hero_data (list[dict[str, Any]]): json hero data
        """
        super().__init__(file_path, **kwargs)
        self.hero_data: list[dict[str, Any]] = self._db

    def __iter__(self):
        self._iter = super().__iter__()
        return self

    def __next__(self):
        """
        Wrap the iteration result in a JsonHero to provide easy access to the
            hero information getting iterated over

        Returns:
            JsonHero: a JsonHero representation of a hero
        """
        next_result = self._iter.__next__()
        return JsonHero(next_result)

    @staticmethod
    def parse_file(bot: "AlbedoBot",
                   file_path: Path,
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

        hero_data: list[dict[str, Any]] = []
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
                                               config.objects.hero_alias).first()

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
