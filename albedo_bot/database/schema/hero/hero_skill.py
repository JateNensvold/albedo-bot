from sqlalchemy import Column, ForeignKey, String, Integer, Text, Sequence
from sqlalchemy.orm import relationship
from sqlalchemy import Enum

from albedo_bot.database.schema.base import base


skill_type_values = ("level",
                     "engraving",
                     "ascension",
                     "si",
                     "furn")
SKILL_TYPE_ENUM = Enum(*skill_type_values, name="skill_type_enum")


class HeroSkill(base):
    """_summary_

    Args:
        Base (_type_): _description_
    """

    __tablename__ = "hero_skills"
    skill_id = Column(Integer,  Sequence("hero_skill_id_seq"), unique=True)
    hero_id = Column(Integer, ForeignKey("heroes.id"), primary_key=True)
    skill_name = Column(String, primary_key=True)
    description = Column(Text)
    skill_image = Column(String)
    skill_type = Column(SKILL_TYPE_ENUM)
    skill_unlock = Column(String)
    checklist_hero = relationship("HeroSkillUpgrade")

    def __repr__(self) -> str:
        """[summary]

        Returns:
            str: [description]
        """
        return f"HeroSkill<{self.id}, {self.skill_name}>"


class HeroSkillUpgrade(base):
    """_summary_

    Args:
        base (_type_): _description_
    """
    __tablename__ = "hero_skills_upgrade"
    skill_id = Column(Integer, ForeignKey(
        "hero_skills.skill_id"), primary_key=True)
    description = Column(Text)
    skill_unlock = Column(String, primary_key=True)
    unlock_type = Column(SKILL_TYPE_ENUM, primary_key=True)

    def __repr__(self) -> str:
        """[summary]

        Returns:
            str: [description]
        """
        return (f"HeroSkillUpgrade<{self.skill_id}, "
                f"{self.skill_unlock}, {self.unlock_type}>")
