
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from albedo_bot.schema.base import Base


class Guild(Base):
    """[summary]
    """

    __tablename__ = "guilds"
    guild_id = Column(Integer, primary_key=True)
    name = Column(String())
    mention = Column(String())
    players = relationship("Players")

    def __repr__(self) -> str:
        """[summary]

        Returns:
            str: [description]
        """
        return f"{self.guild_id}, {self.name}, {self.mention}"
