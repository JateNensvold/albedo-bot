import datetime

from sqlalchemy import Column, ForeignKey, String, BIGINT, DateTime, Integer
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SQLEnum

from albedo_bot.database.schema.base import base
from albedo_bot.utils.enums.timezone_enum import TIMEZONE_ENUM

class Player(base):
    """
    AlbedoBot player Schema
    """

    __tablename__ = "players"
    discord_id = Column(BIGINT, primary_key=True)
    name = Column(String)
    guild_id = Column(BIGINT, ForeignKey("guilds.discord_id",
                      ondelete="RESTRICT"), nullable=False)
    access_time = Column(DateTime, default=datetime.datetime.utcnow)
    resonating_crystal_level = Column(Integer, default=0)
    timezone = Column(SQLEnum(TIMEZONE_ENUM))

    hero_instances = relationship("HeroInstance")
    availability = relationship("PlayerAvailability")
    elder_tree = relationship("PlayerElderTree")

    def mention(self):
        """_summary_
        """
        return f"<@{self.discord_id}>"

    def __repr__(self) -> str:
        """[summary]

        Returns:
            str: [description]
        """
        return f"Player<discord_id={self.discord_id}, name={self.name}>"
