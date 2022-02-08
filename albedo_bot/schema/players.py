from sqlalchemy import Column, ForeignKey, String, Integer
from sqlalchemy.orm import relationship

from albedo_bot.schema.base import Base


class Players(Base):
    """[summary]
    """

    __tablename__ = "players"
    discord_id = Column(Integer, primary_key=True)
    name = Column(String())
    mention = Column(String())
    guild_id = Column(Integer, ForeignKey("guilds.guild_id"))
    hero_instances = relationship("HeroInstance")

    def __repr__(self) -> str:
        """[summary]

        Returns:
            str: [description]
        """
        return f"{self.id}, {self.name}"
