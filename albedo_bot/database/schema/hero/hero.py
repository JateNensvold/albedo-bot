from typing import TYPE_CHECKING, NamedTuple, Union

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Column, String, Integer, Sequence
from sqlalchemy.orm import relationship

from discord.ext import commands

import albedo_bot.config as config
from albedo_bot.database.schema.base import base
from albedo_bot.cogs.utils.mixins.database_mixin import DatabaseMixin

if TYPE_CHECKING:
    from albedo_bot.bot import AlbedoBot


ascension_tier_values = ("ascended", "legendary")
ASCENSION_TIER_ENUM = SQLEnum(
    *ascension_tier_values, name="ascension_tier_enum")


class FactionValues(NamedTuple):
    """_summary_

    Args:
        NamedTuple (_type_): _description_
    """
    lightbearer: str
    mauler: str
    wilder: str
    graveborn: str
    celestial: str
    hypogean: str
    dimensional: str


faction_values = FactionValues("Lightbearer",
                               "Mauler",
                               "Wilder",
                               "Graveborn",
                               "Celestial",
                               "Hypogean",
                               "Dimensional")
FACTION_ENUM = SQLEnum(*faction_values, name="faction_enum")

class_values = ("Warrior",
                "Tank",
                "Ranger",
                "Mage",
                "Support")
CLASS_ENUM = SQLEnum(*class_values, name="class_enum")

hero_type_values = ("Strength",
                    "Intelligence",
                    "Agility")
HERO_TYPE_ENUM = SQLEnum(*hero_type_values, name="hero_type_enum")


class Hero(base, commands.Converter, DatabaseMixin):
    """[summary]
    """

    __tablename__ = "heroes"
    id = Column(Integer,  Sequence("hero_id_seq"),
                primary_key=True, unique=True)
    name = Column(String, unique=True)
    hero_faction = Column(FACTION_ENUM)
    hero_class = Column(CLASS_ENUM)
    hero_type = Column(HERO_TYPE_ENUM)
    ascension_tier = Column(ASCENSION_TIER_ENUM)
    hero_portrait = Column(String)

    hero_instances = relationship("HeroInstance")
    checklist_hero = relationship("ChecklistHero")
    checklist_hero = relationship("HeroFurniture")
    checklist_hero = relationship("HeroFurnitureUpgrade")
    checklist_hero = relationship("HeroSignatureItem")
    checklist_hero = relationship("HeroSignatureItemUpgrade")
    checklist_hero = relationship("HeroSkill")

    def __repr__(self) -> str:
        """[summary]

        Returns:
            str: [description]
        """
        return f"Hero<{self.id}, {self.name}>"

    def full_repr(self):
        """_summary_
        """
        return (f"Hero<{self.id}, {self.name}, {self.hero_faction}, "
                f"{self.hero_class}, {self.hero_type}, {self.ascension_tier}, "
                f"{self.hero_portrait}>")

    async def convert(self, ctx: commands.Context, argument: Union[str, int]):
        """
        Convert a hero Name or id into a database Hero object

        Args:
            ctx (Context): _description_
            argument (Union[str, int]): _description_

        Raises:
            BadArgument: Occurs when a string or integer that is not
                associated with a hero is provided

        Returns:
            Hero: returns the hero associated with the conversion argument that
                was provided
        """
        hero_alias = config.hero_alias

        self.bot: "AlbedoBot" = ctx.bot
        try:
            try:
                int_argument = int(argument)
                hero_instance_select = self.db_select(
                    Hero).where(Hero.id == int_argument)
                hero_instance_result = await self.db_execute(
                    hero_instance_select).first()
            except ValueError as exception:
                hero_instances_select = self.db_select(
                    Hero).where(Hero.name.ilike(f"{argument}%"))
                hero_instances_result = await self.db_execute(
                    hero_instances_select).all()
                if len(hero_instances_result) == 1:
                    hero_instance_result = hero_instances_result[0]
                elif len(hero_instances_result) == 0 and argument in hero_alias:
                    hero_database_name = hero_alias.get(argument)
                    hero_instance_select = self.db_select(Hero).where(
                        Hero.name == hero_database_name)
                    hero_instance_result = await self.db_execute(
                        hero_instance_select).first()
                else:
                    raise commands.BadArgument(
                        f"Invalid hero name `{argument}` too  many `Hero` "
                        f"matches ({hero_instances_result})") from exception
            if hero_instance_result is None:
                raise AssertionError
            return hero_instance_result
        except AssertionError as exception:
            raise commands.BadArgument(
                f"Invalid hero name or id `{argument}`") from exception
