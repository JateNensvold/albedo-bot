from typing import Type
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Column, String, Integer, Sequence
from sqlalchemy.orm import relationship

from albedo_bot.database.schema.base import base
from albedo_bot.cogs.utils.mixins.database_mixin import (
    DatabaseMixin)
from albedo_bot.utils.enums.ascension_type_enum import HeroAscensionEnum
from albedo_bot.utils.enums.hero_faction_enum import HeroFactionEnum
from albedo_bot.utils.enums.hero_class_enum import HeroClassEnum
from albedo_bot.utils.enums.hero_type_enum import HeroTypeEnum


ASCENSION_TYPE_ENUM = SQLEnum(HeroAscensionEnum)
FACTION_ENUM = SQLEnum(HeroFactionEnum)
CLASS_ENUM = SQLEnum(HeroClassEnum)
HERO_TYPE_ENUM = SQLEnum(HeroTypeEnum)


class Hero(base, DatabaseMixin):
    """
    An AFK Arena hero
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
