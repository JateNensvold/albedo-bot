from sqlalchemy import Column, String, Integer, Sequence
from sqlalchemy.orm import relationship

from albedo_bot.schema.base import Base


class Hero(Base):
    """[summary]
    """

    __tablename__ = "heroes"
    id = Column(Integer,  Sequence("hero_id_seq"), primary_key=True)
    name = Column(String, unique=True)
    hero_faction = Column(Integer)
    hero_class = Column(Integer)
    hero_type = Column(Integer)
    ascension_type = Column(Integer)
    hero_portrait = Column(String)

    hero_instances = relationship("HeroInstance")
    checklist_hero = relationship("ChecklistHero")
    checklist_hero = relationship("HeroSkill")
    checklist_hero = relationship("HeroSkill")
    checklist_hero = relationship("HeroSkill")
    checklist_hero = relationship("HeroSkill")
    checklist_hero = relationship("HeroSkill")


    def __repr__(self) -> str:
        """[summary]

        Returns:
            str: [description]
        """
        return f"Hero<{self.id}, {self.name}>"
