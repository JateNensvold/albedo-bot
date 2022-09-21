from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple

import cv2
from image_processing.afk.hero.hero_data import HeroImage
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean
from sqlalchemy.ext.asyncio import AsyncSession

from albedo_bot.database.schema.base import base
from albedo_bot.cogs.utils.mixins.database_mixin import DatabaseMixin
from albedo_bot.database.schema.hero.hero import Hero
from albedo_bot.utils.errors import DatabaseError, MessageError, PreCommitException
from albedo_bot.utils.files.image_util import ContentType
from albedo_bot.utils.message.message_send import EmbedWrapper

if TYPE_CHECKING:
    from albedo_bot.bot import AlbedoBot


class PortraitType(Enum):
    """
    An enumeration of all the ways that a portraits requirement status can be
    specified in a file name
    """
    required: bool = True
    optional: bool = False


class PortraitResults(NamedTuple):
    """
    A wrapper class for portrait results fetched from the database
    """

    required_portraits: tuple["HeroPortrait"]
    optional_portraits: tuple["HeroPortrait"]

    def __len__(self):
        return len(self.required_portraits) + len(self.optional_portraits)


class PortraitNameInfo(NamedTuple):
    """
    A wrapper class for all the information stored in a HeroPortraits name
    """
    hero_name: str
    required: str
    image_index: int
    extension: str

    def __str__(self):
        """
        Generate a file name from all the stored information
        """

        return ".".join([self.hero_name, str(self.required),
                         str(self.image_index), str(self.extension)])

    @classmethod
    def from_str(cls, image_name: str):
        """
        Generate a PortraitNameInfo object from a portrait `image_name`

        Args:
            image_name (str): a HeroPortrait image_name

        Returns:
            PortraitNameInfo: a newly initialized PortraitNameInfo
        """
        print(image_name)
        hero_name, required, image_index, extension = image_name.split(".")
        required = PortraitType[required].value
        image_index = int(image_index)
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

    def pre_commit(self):
        """
        A pre commit hook that runs before a HeroPortrait is added
        to the database
        """

        full_path = self.full_path()
        if not full_path.exists():
            raise PreCommitException(f"`{full_path}` does not exist")

    @property
    def hero_name(self):
        """
        Attempt to parse the hero_name from image_name
        """
        name_info = PortraitNameInfo.from_str(self.image_name)
        return name_info.hero_name

    def __str__(self):
        """
        A str representation for a HeroPortrait object
        """

        return (f"HeroPortrait<{self.full_path()} - "
                f"R={self.required},I={self.image_index}>")

    def full_path(self):
        """
        Return the full file path as a Path object
        """

        return Path(self.image_directory, self.image_name)

    async def get_hero_portraits(self, hero: Hero, session: AsyncSession = None):
        """
        Fetch all hero portraits for `hero`

        Args:
            hero (Hero): hero to fetch portraits for

        Returns:
            PortraitResults: all the HeroPortraits for a `hero` inside a
                PortraitResults object
        """

        if session is not None:
            self.session = session

        if not self.has_session():
            raise DatabaseError(
                "Unable to find a way to connect to database, "
                "provide a valid session or set the session on the object "
                "calling this function")

        portraits_select = self.db_select(
            HeroPortrait).where(hero.id == HeroPortrait.id)

        hero_portraits = await self.db_execute(portraits_select).all()

        required_portraits: list[HeroPortrait] = []
        optional_portraits: list[HeroPortrait] = []

        for hero_portrait in hero_portraits:
            if hero_portrait.required:
                required_portraits.append(hero_portrait)
            else:
                optional_portraits.append(hero_portrait)

        optional_portraits.sort(key=lambda portrait: portrait.image_index)
        return PortraitResults(required_portraits, optional_portraits)

    async def build_hero_image(self, session: AsyncSession):
        """
        Build a HeroImage object from

        Args:
            session (AsyncSession): session connection to databases

        Returns:
            HeroImage: HeroImage that was built
        """
        self.session = session

        hero_select = self.db_select(Hero).where(Hero.id == self.id)
        hero_object = await self.db_execute(hero_select).first()

        hero_image = cv2.imread(str(self.full_path()))
        hero_name = hero_object.name.lower()
        return HeroImage(hero_name, hero_image, self.full_path())

    @ classmethod
    async def get_portrait(cls, hero: Hero, session: AsyncSession):
        """
        Get the first "required" portrait associated with a hero

        Args:
            hero (Hero): hero to get portrait for
            session (AsyncSession): connection with database

        Returns:
            HeroPortrait: a HerPortrait of the hero
        """

        # Dummy portrait used to interact with database
        hero_portrait = HeroPortrait()
        hero_portrait.session = session

        select_portrait = hero_portrait.db_select(
            HeroPortrait).where(HeroPortrait.id == hero.id,
                                HeroPortrait.required == True,
                                HeroPortrait.image_index == 0)

        return await hero_portrait.db_execute(select_portrait).first()

    @ classmethod
    def build_name(cls, hero: Hero, portrait_results: PortraitResults,
                   content_type: ContentType,
                   portrait_type: PortraitType = PortraitType.required):
        """
        Build a portrait name for an image

        Args:
            hero (Hero): hero to build a name for
            portrait_results (PortraitResults): currently stored portraits
                in database
            content_type (ContentType): type of image/content to build name for
            portrait_type (PortraitType, optional): flag describing the type
                of portrait to build a name for.
                Defaults to PortraitType.required

        Returns:
            (str): new portrait name
        """
        if portrait_type == PortraitType.required:
            portrait_count = len(portrait_results.optional_portraits)
        else:
            portrait_count = len(portrait_results.required_portraits)

        portrait_name_info = PortraitNameInfo(
            hero.name.lower(), portrait_type.name,
            portrait_count, content_type.extension_type)

        return str(portrait_name_info)

    @ classmethod
    async def add_portrait(cls, bot: "AlbedoBot", hero: Hero,
                           portrait_directory_path: Path,
                           content_type: ContentType,
                           hero_index: int,
                           image_data: bytes,
                           is_required: bool):
        """
        Create a hero portrait and adds it into the portrait database.
        Also flushes image_data to location referred to by new HeroPortrait that
        is created. When need will adjust the index of all other portraits that
        get their position bumped by the new portrait

        Args:
            hero (Hero): hero to add portrait for
            portrait_directory_path (Path): directory of hero portrait
            content_type (ContentType): extension/content type of portrait
            hero_index (int): index to create portrait at
            image_data (bytes): image/image data to associate with the new
                HeroPortrait
            is_required (bool): boolean flag signifying if the portrait getting
                added is required(true) or optional(false)

        Raises:
            MessageError: If image already exists at portrait path generated
                for portrait
            MessageError: If directory for portrait does not exist

        Returns:
            HeroPortrait: newly created portrait
        """

        new_portrait = HeroPortrait()
        new_portrait.bot = bot

        portrait_results = await new_portrait.get_hero_portraits(hero)

        update_portraits: list[HeroPortrait] = []

        if is_required:
            portrait_count = len(portrait_results.required_portraits)
            portrait_list = portrait_results.required_portraits
            portrait_type = PortraitType.required
        else:
            portrait_count = len(portrait_results.optional_portraits)
            portrait_list = portrait_results.optional_portraits
            portrait_type = PortraitType.optional
        if hero_index < 0:
            hero_index = portrait_count
        elif hero_index > portrait_count:
            hero_index = portrait_count
        else:
            for hero_portrait in portrait_list:
                if hero_portrait.image_index >= hero_index:
                    hero_portrait.image_index += 1
                    update_portraits.append(hero_portrait)

        portrait_name = cls.build_name(hero, portrait_results, content_type,
                                       portrait_type)

        new_portrait.image_index = hero_index
        new_portrait.required = is_required
        new_portrait.image_directory = str(portrait_directory_path)
        new_portrait.image_name = portrait_name
        new_portrait.id = hero.id

        full_portrait_path = new_portrait.full_path()

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

        try:
            with open(full_portrait_path, 'wb') as file_pointer:
                file_pointer.write(image_data)

            await bot.db_add(new_portrait)

            for hero_portrait_update in update_portraits:
                await bot.db_add(hero_portrait_update)
        except Exception as exception:
            # When exception occurs while adding portrait to DB wipe the newly
            #   written image from disk
            full_portrait_path.unlink()
            raise exception

        return new_portrait
