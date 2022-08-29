from typing import Type

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Column, String, Integer, Sequence
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncSession

from albedo_bot.database.schema.base import base
from albedo_bot.cogs.utils.mixins.database_mixin import (
    DatabaseMixin, ScalarWrapper)
from albedo_bot.utils.enums.ascension_type_enum import HeroAscensionEnum
from albedo_bot.utils.enums.hero_faction_enum import HeroFactionEnum
from albedo_bot.utils.enums.hero_class_enum import HeroClassEnum
from albedo_bot.utils.enums.hero_type_enum import HeroTypeEnum
from albedo_bot.utils.config import Config


ASCENSION_TYPE_ENUM = SQLEnum(HeroAscensionEnum)
FACTION_ENUM = SQLEnum(HeroFactionEnum)
CLASS_ENUM = SQLEnum(HeroClassEnum)
HERO_TYPE_ENUM = SQLEnum(HeroTypeEnum)


class Hero(base, DatabaseMixin):
    """
    A database representation of an AFK Arena hero
    """

    __tablename__ = "heroes"
    id = Column(Integer,  Sequence("hero_id_seq"),
                primary_key=True, unique=True)
    name = Column(String, unique=True)
    hero_faction: HeroFactionEnum = Column(FACTION_ENUM)
    hero_class = Column(CLASS_ENUM)
    hero_type = Column(HERO_TYPE_ENUM)
    ascension_tier = Column(ASCENSION_TYPE_ENUM)

    hero_instances = relationship("HeroInstance")
    checklist_hero = relationship("ChecklistHero")
    hero_furniture = relationship("HeroFurniture")
    hero_furniture_upgrade = relationship("HeroFurnitureUpgrade")
    hero_signature_item = relationship("HeroSignatureItem")
    hero_signature_item_upgrade = relationship("HeroSignatureItemUpgrade")
    hero_skill = relationship("HeroSkill")
    hero_portrait = relationship("HeroPortrait")

    @classmethod
    def ilike(cls, session: AsyncSession, hero_name: str,
              hero_alias: Config = None):
        """
        Return a ScalarWrapper for heroes with the most similar names
        to `hero_name`. If a `hero_alias` config is provided then hero_name
        will match against any hero_alias that have been configured

        Args:
            session (AsyncSession): connection with database
            hero_name (str): name to match to most similar heroes name
            hero_alias (Config, optional): Alias Config for a hero.
                Defaults to None.

        Returns:
            ScalarWrapper[Type[Hero]]: a ScalarWrapper around a hero result
        """

        if hero_alias and hero_name in hero_alias:
            hero_name = hero_alias.get(hero_name)

        database_wrapper = DatabaseMixin()
        database_wrapper.session = session
        hero_select_statement = database_wrapper.db_select(
            Hero).where(Hero.name.ilike(f"{hero_name}%"))
        return database_wrapper.db_execute(hero_select_statement)

    def __repr__(self) -> str:
        """
        Fast representation of Hero for quick identification of Hero Object

        Returns:
            str: [description]
        """
        return f"Hero<{self.id}, {self.name}>"

    def __str__(self):
        """
        String representation of Hero that is human readable

        Returns:
            str: human readable string with hero information
        """
        return (f"{self.id} {self.name} - ({self.hero_faction}, "
                f"{self.hero_class}, {self.hero_type}, {self.ascension_tier})")

    def full_repr(self):
        """
        Representation of Hero with all information 
        """
        return (f"Hero<{self.id}, {self.name}, {self.hero_faction}, "
                f"{self.hero_class}, {self.hero_type}, {self.ascension_tier}, "
                f"{self.hero_portrait}>")
