from sqlalchemy import Column, String, Integer, Sequence
from sqlalchemy.orm import relationship

from albedo_bot.schema.base import Base


class Heroes(Base):
    """[summary]
    """

    __tablename__ = "heroes"
    id = Column(Integer,  Sequence("hero_id_seq"), primary_key=True)
    name = Column(String())
    hero_instances = relationship("HeroInstance")

    def __repr__(self) -> str:
        """[summary]

        Returns:
            str: [description]
        """
        return f"{self.id}, {self.name}"
