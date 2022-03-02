
from sqlalchemy import Column, ForeignKey, String
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
    hero_name = Column(String, ForeignKey("Checklist.name"), primary_key=True)

    def __repr__(self) -> str:
        """[summary]

        Returns:
            str: [description]
        """
        return f"ChecklistHero<{self.checklist_name}, {self.hero_name}>"
