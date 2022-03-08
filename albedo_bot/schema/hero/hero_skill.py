from sqlalchemy import Column, ForeignKey, String, Integer, Text

from albedo_bot.schema.base import Base


class HeroSkill(Base):
    """_summary_

    Args:
        Base (_type_): _description_
    """

    __tablename__ = "hero_skills"
    id = Column(Integer, ForeignKey("heroes.id"), primary_key=True)
    skill_name = Column(String, primary_key=True)
    description = Column(Text)
    skill_image = Column(String)
    skill_unlock = Column(Integer)

    def __repr__(self) -> str:
        """[summary]

        Returns:
            str: [description]
        """
        return f"HeroSkill<{self.id}, {self.skill_name}>"


class HeroSkillUpgrade(Base):
    """_summary_

    Args:
        Base (_type_): _description_
    """
    __tablename__ = "hero_skills_upgrade"
    id = Column(Integer, ForeignKey("heroes.id"), primary_key=True)
    skill_name = Column(String, ForeignKey(
        "hero_skills.skill_name"))
    description = Column(Text)
    skill_unlock = Column(Integer, primary_key=True)
    unlock_type = Column(Integer, primary_key=True)

    def __repr__(self) -> str:
        """[summary]

        Returns:
            str: [description]
        """
        return (f"HeroSkillUpgrade<{self.id}, {self.skill_name}, "
                f"{self.skill_unlock}, {self.unlock_type}>")
