from typing import NamedTuple
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Column, String, Integer, Sequence
from sqlalchemy.orm import relationship

from albedo_bot.schema.base import Base


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


class Hero(Base):
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
