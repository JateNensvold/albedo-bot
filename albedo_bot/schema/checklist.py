
from sqlalchemy import Column, ForeignKey, String, Integer, BIGINT
from sqlalchemy.orm import relationship

from albedo_bot.schema.base import Base


class Checklist(Base):
    """[summary]
    """

    __tablename__ = "checklists"
    name = Column(String, primary_key=True)
    description = Column(String)
    checklist_hero = relationship("ChecklistHero")

    def __repr__(self) -> str:
        """[summary]

        Returns:
            str: [description]
        """
        return f"Checklist<{self.name}>"


class ChecklistHero(Base):
    """[summary]
    """

    __tablename__ = "checklist_heroes"
    checklist_name = Column(
        String, ForeignKey("checklists.name"), primary_key=True)
    hero_id = Column(BIGINT, ForeignKey("heroes.id"), primary_key=True)

    signature_level = Column(Integer)
    furniture_level = Column(Integer)
    ascension_level = Column(Integer)
    engraving_level = Column(Integer)

    def __repr__(self) -> str:
        """[summary]

        Returns:
            str: [description]
        """
        return f"ChecklistHero<{self.checklist_name}, {self.hero_name}>"
