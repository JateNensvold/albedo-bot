from sqlalchemy import Column, ForeignKey, String, Integer, BIGINT
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SQLEnum

from albedo_bot.database.schema.base import base
from albedo_bot.cogs.utils.mixins.database_mixin import DatabaseMixin
from albedo_bot.utils.enums.ascension_enum import AscensionValues


class Checklist(base, DatabaseMixin):
    """[summary]
    """

    __tablename__ = "checklists"
    name = Column(String, primary_key=True)
    description = Column(String)
    checklist_hero = relationship("ChecklistHero", cascade="all,delete")

    def __repr__(self) -> str:
        """[summary]

        Returns:
            str: [description]
        """
        return f"Checklist<{self.name}>"


class ChecklistHero(base):
    """[summary]
    """

    __tablename__ = "checklist_heroes"
    checklist_name = Column(
        String, ForeignKey("checklists.name"), primary_key=True)
    hero_id = Column(BIGINT, ForeignKey("heroes.id"), primary_key=True)

    signature_level = Column(Integer)
    furniture_level = Column(Integer)
    ascension_level = Column(SQLEnum(AscensionValues, name="ascension_enum"))
    engraving_level = Column(Integer)

    def __repr__(self) -> str:
        """[summary]

        Returns:
            str: [description]
        """
        return f"ChecklistHero<{self.checklist_name}, {self.hero_id}>"
