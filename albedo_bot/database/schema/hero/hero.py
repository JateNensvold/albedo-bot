from typing import TYPE_CHECKING, Union

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Column, String, Integer, Sequence
from sqlalchemy.orm import relationship

from discord.ext import commands

from albedo_bot.database.schema.base import base
from albedo_bot.cogs.utils.mixins.database_mixin import DatabaseMixin
from albedo_bot.utils.enums.ascension_type_enum import HeroAscensionEnum
from albedo_bot.utils.enums.hero_faction_enum import HeroFactionEnum
from albedo_bot.utils.enums.hero_class_enum import HeroClassEnum
from albedo_bot.utils.enums.hero_type_enum import HeroTypeEnum


if TYPE_CHECKING:
    from albedo_bot.bot import AlbedoBot

ASCENSION_TYPE_ENUM = SQLEnum(HeroAscensionEnum)
FACTION_ENUM = SQLEnum(HeroFactionEnum)
CLASS_ENUM = SQLEnum(HeroClassEnum)
HERO_TYPE_ENUM = SQLEnum(HeroTypeEnum)

# commands.Converter,


class Hero(base, DatabaseMixin):
    """[summary]
    """

    __tablename__ = "heroes"
    id = Column(Integer,  Sequence("hero_id_seq"),
                primary_key=True, unique=True)
    name = Column(String, unique=True)
    hero_faction: HeroFactionEnum = Column(FACTION_ENUM)
    hero_class = Column(CLASS_ENUM)
    hero_type = Column(HERO_TYPE_ENUM)
    ascension_tier = Column(ASCENSION_TYPE_ENUM)
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

    def __str__(self):
        return (f"{self.id} {self.name} - ({self.hero_faction}, "
                f"{self.hero_class}, {self.hero_type}, {self.ascension_tier})")

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
        import albedo_bot.config as config
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
                    Hero).where(Hero.name == argument)
                hero_instances_result = await self.db_execute(
                    hero_instances_select).all()
                if len(hero_instances_result) == 1:
                    return hero_instances_result[0]

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
                elif len(hero_instances_result) == 0:
                    raise commands.BadArgument(
                        (f"Invalid hero name `{argument}` no hero matches "
                         "that name")) from exception
                else:
                    hero_names = [f"(\"{hero.name}\", {hero.id})"
                                  for hero in hero_instances_result]
                    hero_names_str = ", ".join(hero_names)
                    raise commands.BadArgument(
                        f"Invalid hero name `{argument}` too many Hero "
                        "matches. Choose one of the following heroes "
                        f"`[{hero_names_str}]`") from exception
            if hero_instance_result is None:
                raise AssertionError
            return hero_instance_result
        except AssertionError as exception:
            raise commands.BadArgument(
                f"Invalid hero name or id `{argument}`") from exception
