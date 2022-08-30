import os
from dataclasses import dataclass
from typing import Union, TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, BIGINT
from sqlalchemy import Enum as SQLEnum

from discord.ext import commands

from albedo_bot.utils import emoji
from albedo_bot.cogs.utils.mixins.database_mixin import DatabaseMixin
from albedo_bot.cogs.utils.mixins.enum_mixin import EnumMixin
from albedo_bot.cogs.utils.mixins.emoji_mixin import EmojiMixin
from albedo_bot.database.schema.base import base
from albedo_bot.database.schema.hero.hero import Hero
from albedo_bot.utils.emoji import busts_in_silhouette
from albedo_bot.cogs.checklist.utils.missing_hero import MissingHero
from albedo_bot.utils.enums.ascension_enum import AscensionValues

if TYPE_CHECKING:
    from albedo_bot.bot import AlbedoBot
    from albedo_bot.database.schema.checklist import ChecklistHero


class HeroUpdateStatus(EnumMixin):
    """_summary_

    Args:
        Enum (_type_): _description_

    Returns:
        _type_: _description_
    """
    NO_UPDATED_HERO = " "
    UPDATED_HERO = "~"
    NEW_HERO = "+"


@dataclass
class HeroInstanceData:
    """_summary_

    Args:
        namedtuple (_type_): _description_

    Returns:
        _type_: _description_
    """
    hero_name: str
    hero_id: int
    signature_level: int
    furniture_level: int
    ascension_level: AscensionValues
    engraving_level: int
    hero_update_status: HeroUpdateStatus = HeroUpdateStatus.NO_UPDATED_HERO

    @staticmethod
    async def from_hero_instance(db_handle: DatabaseMixin,
                                 hero_instances: list["HeroInstance"]):
        """
        Convert a list of `HeroInstance` into a list of `HeroInstanceData`

        Args:
            db_handle (DatabaseMixin): connection to the hero database for
                fetching additional hero information
            hero_instances (list[&quot;HeroInstance&quot;]): list of
                HeroInstance to be converted

        Returns:
            list[HeroInstanceData]: a list of HeroInstanceData's
        """

        hero_instance_tuple_list: list[HeroInstanceData] = []

        # Convert hero_instances into a list if only a single hero_instance
        #   was provided
        if not isinstance(hero_instances, list):
            hero_instances = [hero_instances]

        for hero_instance in hero_instances:
            hero_select = db_handle.db_select(Hero).where(
                Hero.id == hero_instance.hero_id)

            hero_object = await db_handle.db_execute(hero_select).first()
            hero_instance_tuple_list.append(
                HeroInstanceData(hero_object.name, hero_instance.hero_id,
                                 hero_instance.signature_level,
                                 hero_instance.furniture_level,
                                 hero_instance.ascension_level,
                                 hero_instance.engraving_level))

        return hero_instance_tuple_list

    @staticmethod
    async def from_checklist_hero(db_handle: DatabaseMixin,
                                  checklist_heroes: list["ChecklistHero"]):
        """_summary_

        Args:
            db_handle (DatabaseMixin): _description_
            checklist_heroes (list[&quot;HeroInstance&quot;]): _description_
        """
        hero_instance_tuple_list: list[HeroInstanceData] = []

        # Convert hero_instances into a list if only a single hero_instance
        #   was provided
        if not isinstance(checklist_heroes, list):
            checklist_heroes = [checklist_heroes]

        for checklist_hero in checklist_heroes:
            hero_select = db_handle.db_select(Hero).where(
                Hero.id == checklist_hero.hero_id)

            hero_object = await db_handle.db_execute(hero_select).first()
            hero_instance_tuple_list.append(
                HeroInstanceData(hero_object.name,
                                 checklist_hero.hero_id,
                                 checklist_hero.signature_level,
                                 checklist_hero.furniture_level,
                                 checklist_hero.ascension_level,
                                 checklist_hero.engraving_level))
        return hero_instance_tuple_list

    def __eq__(self, comparator: "HeroInstanceData") -> bool:
        return self.ascension_level.value == comparator.ascension_level.value

    def __lt__(self, comparator: "HeroInstanceData") -> bool:
        return self.ascension_level.value < comparator.ascension_level.value

    def __le__(self, comparator: "HeroInstanceData") -> bool:
        return self.ascension_level.value <= comparator.ascension_level.value

    def __gt__(self, comparator: "HeroInstanceData") -> bool:
        return self.ascension_level.value > comparator.ascension_level.value

    def __ge__(self, comparator: "HeroInstanceData") -> bool:
        return self.ascension_level.value >= comparator.ascension_level.value


class HeroList(DatabaseMixin, EmojiMixin):
    """_summary_
    """

    heroes_title_str = "Heroes"

    def __init__(self, bot: "AlbedoBot",
                 heroes: list[Union[HeroInstanceData, MissingHero]]):
        """
        A wrapper around a list of `HeroInstanceData` heroes that is used to
        generate a string containing all the hero information for discord
        messages

        Args:
            bot (AlbedoBot): current discord bot
            heroes (List[HeroInstanceData]): list of hero information
            longest_name (int, optional): An optional parameter that represents
                a new longest name length to use when generating the spacing
                for hero attributes in the formatted string. Defaults to None.
            skip_header (bool, optional): An optional flag that will skip
                adding the formatted string header when generating the hero
                string. Defaults to False.
        """

        # Set self.bot for DatabaseMixin
        self.bot = bot
        if len(heroes) > 0 and isinstance(heroes[0], MissingHero):
            longest_name_list: list[str] = []
            for missing_heroes in heroes:
                longest_name_list.append(
                    missing_heroes.checklist_hero.hero_name)
        else:
            longest_name_list = [hero.hero_name for hero in heroes]
        longest_name_list.append(self.heroes_title_str)

        self.longest_name = len(max(longest_name_list, key=len))
        self.longest_prefix_len = 0
        self.heroes = heroes

    async def format_heroes(self,
                            checklist_hero_prefix: str = "",
                            hero_instance_prefix: str = ""):
        """
        Generate a list of hero attribute strings


        Args:
            checklist_hero_prefix (str, optional): a checklist hero prefix that
                is used when using a list of MissingHero. Defaults to "".
            hero_instance_prefix (str, optional): a hero instance prefix that
                is used when using a list of MissingHero. Defaults to "".
        """
        formatted_heroes = []

        hero_update_space = " "
        hero_prefix_space = " "

        self.longest_prefix_len = max(len(checklist_hero_prefix),
                                      len(hero_instance_prefix))

        if self.longest_prefix_len == 0:
            header_prefix_str = ""
        else:
            header_prefix_str = (f"`{self.longest_prefix_len * '-'}`"
                                 f"{hero_prefix_space}")
        formatted_heroes.append(
            (f"{header_prefix_str}"
             f"{busts_in_silhouette}{hero_update_space}`"
             f"{self.heroes_title_str: <{self.longest_name}} "
             "ASC SI FI ENGRAVING`")
        )

        for hero_tuple in self.heroes:

            if isinstance(hero_tuple, MissingHero):
                hero_id = hero_tuple.checklist_hero.hero_id
            else:
                hero_id = hero_tuple.hero_id

            hero_select = self.db_select(Hero).where(
                Hero.id == hero_id)
            hero_result = await self.db_execute(hero_select).first()

            try:
                # portrait_name, _portrait_extension = os.path.splitext(
                #     os.path.basename(hero_result.hero_portrait))
                hero_emoji = str(self.get_emoji(hero_result.emoji_name()))
            # pylint: disable=broad-except
            except Exception as _exception:
                hero_emoji = emoji.grey_question

            if isinstance(hero_tuple, MissingHero):
                checklist_hero_str = self.hero_str(
                    hero_tuple.checklist_hero,
                    hero_emoji,
                    checklist_hero_prefix)
                formatted_heroes.append(checklist_hero_str)
                if hero_tuple.hero_instance is not None:
                    hero_instance_str = self.hero_str(
                        hero_tuple.hero_instance,
                        hero_emoji,
                        hero_instance_prefix)
                    formatted_heroes.append(hero_instance_str)
                else:
                    formatted_heroes.append(
                        f"`{hero_instance_prefix: <{self.longest_prefix_len}}`")
            else:
                hero_str = self.hero_str(hero_tuple, hero_emoji, "")
                formatted_heroes.append(hero_str)
        message = "\n".join(formatted_heroes)
        output = f"{message}"
        return output

    def hero_str(self, hero_tuple: HeroInstanceData, emoji_str: str,
                 prefix: str):
        """
        Generate a hero attribute string

        Args:
            hero_tuple (HeroInstanceData): _description_
        """
        if len(prefix) == 0:
            prefix_str = ""
        else:
            prefix_str = f"`{prefix: <{self.longest_prefix_len}}` "

        hero_str = (
            f"{prefix_str}"
            f"{emoji_str} "
            # f"{hero_tuple.hero_update_status.value} "
            f"`{hero_tuple.hero_name: <{self.longest_name}} "
            f"{hero_tuple.ascension_level.name: <{3}} "
            f"{hero_tuple.signature_level: <2} "
            f"{hero_tuple.furniture_level: <2} "
            f"{hero_tuple.engraving_level}`")
        return hero_str

    def __str__(self):
        """_summary_
        """
        return f"HeroList<{len(self.heroes)} heroes long>"

    async def async_str(self):
        """
        Create a string all all the heroes in HeroList
        """
        output = await self.format_heroes()
        return output


class HeroInstance(base, DatabaseMixin):
    """[summary]

    Args:
        base ([type]): [description]

    Returns:
        [type]: [description]
    """

    __tablename__ = "hero_instances"
    hero_id = Column(Integer, ForeignKey("heroes.id"), primary_key=True)
    player_id = Column(BIGINT, ForeignKey(
        "players.discord_id"), primary_key=True)
    signature_level = Column(Integer)
    furniture_level = Column(Integer)
    ascension_level = Column(SQLEnum(AscensionValues, name="ascension_enum"))
    engraving_level = Column(Integer)

    def __init__(self, hero_id: int, player_id: int, signature_level: int,
                 furniture_level: int, ascension_level: AscensionValues,
                 engraving_level: int):
        self.hero_id = hero_id
        self.player_id = player_id
        self.signature_level = int(signature_level)
        self.furniture_level = int(furniture_level)
        self.ascension_level = ascension_level
        self.engraving_level = int(engraving_level)

    def __repr__(self) -> str:
        """[summary]

        Returns:
            str: [description]
        """
        return f"HeroInstance<hero_id={self.hero_id}, player_id={self.player_id}>"

    def __str__(self) -> str:
        """_summary_

        Returns:
            str: _description_
        """
        return (f"{self.hero_id} {self.ascension_level} "
                f"{self.signature_level}{self.furniture_level} "
                f"{self.engraving_level}")

    async def full_str(self, ctx: commands.Context):
        """
        Generate a human readable string that contains the hero name

        Args:
            ctx (_type_): _description_
        """

        self.bot = ctx.bot
        hero_select = self.db_select(Hero).where(
            Hero.id == self.hero_id)
        hero_result = await self.db_execute(hero_select).first()

        return (f"{hero_result.name}, {self.ascension_level} "
                f"{str(self.signature_level).rjust(2, '0')}"
                f"{self.furniture_level} E={self.engraving_level}")

    def update_from_instance(self, new_instance: "HeroInstance"):
        """
        Update the current hero instance with another HeroInstance Object

        Args:
            now_instance (HeroInstance): _description_
        """
        return self.update(new_instance.signature_level,
                           new_instance.furniture_level,
                           new_instance.ascension_level,
                           new_instance.engraving_level)

    def update(self, signature_level: Union[int, str],
               furniture: Union[int, str], ascension: AscensionValues,
               engraving: Union[int, str]):
        """
        Update self with new values

        Args:
            signature_level (int): _description_
            furniture (int): _description_
            ascension (str): _description_
            engraving (int): _description_

        Returns:
            _type_: _description_
        """
        updated = False
        signature_level = int(signature_level)
        furniture = int(furniture)
        engraving = int(engraving)

        if signature_level > self.signature_level:
            updated = True
            self.signature_level = int(signature_level)
        if furniture > self.furniture_level:
            updated = True
            self.furniture_level = int(furniture)
        if ascension.value > self.ascension_level.value:
            updated = True
            self.ascension_level = ascension
        if engraving > self.engraving_level:
            updated = True
            self.engraving_level = int(engraving)

        return updated

    @staticmethod
    def from_instance_tuple(hero_instance_tuple: HeroInstanceData,
                            player_id: int):
        """
        Creates a HeroInstance from a `HeroInstanceData` and a `player_id`

        Args:
            hero_instance_tuple (HeroInstanceData): object to create new
                HeroInstance from
            player_id (int): player_id to set on new HeroInstance
        """

        return HeroInstance(hero_instance_tuple.hero_id, player_id,
                            hero_instance_tuple.signature_level,
                            hero_instance_tuple.furniture_level,
                            hero_instance_tuple.ascension_level,
                            hero_instance_tuple.engraving_level)

    def __eq__(self, comparator: "HeroInstance") -> bool:
        return self.ascension_level.value == comparator.ascension_level.value

    def __lt__(self, comparator: "HeroInstance") -> bool:
        return self.ascension_level.value < comparator.ascension_level.value

    def __le__(self, comparator: "HeroInstance") -> bool:
        return self.ascension_level.value <= comparator.ascension_level.value

    def __gt__(self, comparator: "HeroInstance") -> bool:
        return self.ascension_level.value > comparator.ascension_level.value

    def __ge__(self, comparator: "HeroInstance") -> bool:
        return self.ascension_level.value >= comparator.ascension_level.value
