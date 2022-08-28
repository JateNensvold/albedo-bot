from enum import Enum
import re
from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple

from sqlalchemy import Column, String, Integer, ForeignKey, Boolean

from albedo_bot.database.schema.base import base
from albedo_bot.cogs.utils.mixins.database_mixin import DatabaseMixin
from albedo_bot.database.schema.hero.hero import Hero
from albedo_bot.utils.errors import MessageError
from albedo_bot.utils.files.image_util import ContentType
from albedo_bot.utils.message import EmbedWrapper

if TYPE_CHECKING:
    from albedo_bot.bot import AlbedoBot


class PortraitRequired(Enum):
    """
    An enumeration of all the ways that a portraits requirement status can be
    specified in a file name
    """
    required: bool = True
    optional: bool = False


class PortraitNameInfo(NamedTuple):
    """
    A wrapper class for all the information stored in a HeroPortraits name
    """
    hero_name: str
    required: bool
    image_index: int
    extension: str

    def __str__(self):
        """
        Generate a file name from all the stored information
        """

        return ".".join([self.hero_name, self.required,
                         self.image_index, self.extension])

    @classmethod
    def from_str(cls, image_name: str):
        """
        Generate a PortraitNameInfo object from a portrait `image_name`

        Args:
            image_name (str): a HeroPortrait image_name

        Returns:
            PortraitNameInfo: a newly initialized PortraitNameInfo
        """

        hero_name, required, image_index, extension = image_name.split(".")
        required = PortraitRequired[required].value
        return PortraitNameInfo(hero_name, required, image_index, extension)


class HeroPortrait(base, DatabaseMixin):
    """
    A hero image/portrait that is associated with a hero
    """

    __tablename__ = "hero_portraits"
    id = Column(Integer, ForeignKey("heroes.id"), primary_key=True)
    image_index = Column(Integer, primary_key=True)
    required = Column(Boolean, primary_key=True)
    image_directory = Column(String)
    image_name = Column(String)

    def full_path(self):
        """
        Return the full file path as a Path object
        """

        return Path(self.image_directory, self.image_name)

    async def get_hero_portraits(self, hero: Hero):
        """
        Fetch all hero portraits for `hero`

        Args:
            hero (Hero): hero to fetch portraits for 

        Returns:
            list[HeroPortrait]: list of all the HeroPortraits for a `hero`
        """
        portraits_select = self.db_select(
            HeroPortrait).where(hero.id == HeroPortrait.id)

        hero_portraits = await self.db_execute(portraits_select).all()
        return hero_portraits

    @classmethod
    async def add_optional(cls, bot: "AlbedoBot", hero: Hero,
                           portrait_directory_path: Path,
                           content_type: ContentType, hero_index: int):
        """
        Create an optional hero portrait and add it into the portrait database,
            also adjusts index of all other portraits that got bumped by the
            new portrait

        Args:
            hero (Hero): hero to add portrait for
            portrait_directory_path (Path): directory of hero portrait
            content_type (ContentType): extension/content type of portrait
            hero_index (int): index to create portrait at

        Raises:
            MessageError: If image already exists at portrait path generated
                for portrait
            MessageError: If directory for portrait does not exist

        Returns:
            HeroPortrait: newly created portrait
        """
        required_portraits: list[HeroPortrait] = []
        optional_portraits: list[HeroPortrait] = []

        new_portrait = HeroPortrait()
        new_portrait.bot = bot

        hero_portraits = await new_portrait.get_hero_portraits(hero)

        for hero_portrait in hero_portraits:
            if hero_portrait.required:
                required_portraits.append(hero_portrait)
            else:
                optional_portraits.append(hero_portrait)

        optional_portraits.sort(key=lambda portrait: portrait.image_index)

        update_portraits: list[HeroPortrait] = []

        if hero_index < 0:
            hero_index = len(optional_portraits)
        elif hero_index > len(optional_portraits):
            hero_index = len(optional_portraits)
        else:
            for hero_portrait in optional_portraits:
                if hero_portrait.image_index >= hero_index:
                    hero_portrait.image_index += 1
                    update_portraits.append(hero_portrait)

        portrait_name = (f"{hero.name}-optional{len(optional_portraits)}."
                         f"{content_type.extension_type}").lower()

        new_portrait.image_index = hero_index
        new_portrait.required = False
        new_portrait.image_directory = str(portrait_directory_path)
        new_portrait.image_name = portrait_name
        new_portrait.id = hero.id

        full_portrait_path = portrait_directory_path.joinpath(
            portrait_name)
        if not portrait_directory_path.exists():
            embed_wrapper = EmbedWrapper(
                title="Portrait Path Failure",
                description=(
                    "The following path does not exist "
                    f"{portrait_directory_path}.\n"
                    f"Contact an admin or {bot.owner_string} with the "
                    "above error"))
            raise MessageError(embed_wrapper=embed_wrapper)
        elif full_portrait_path.exists():
            embed_wrapper = EmbedWrapper(
                title="Portrait Path Failure",
                description=(
                    "The following path already exists "
                    f"`{full_portrait_path}`.\n"
                    f"Contact an admin or {bot.owner_string} with the "
                    "above error"))
            raise MessageError(embed_wrapper=embed_wrapper)

        await bot.db_add(new_portrait)

        for hero_portrait_update in update_portraits:
            await bot.db_add(hero_portrait_update)

        return new_portrait
