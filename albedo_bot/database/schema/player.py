from sqlalchemy import Column, ForeignKey, String, BIGINT
from sqlalchemy.orm import relationship

from albedo_bot.database.schema.base import base


class Player(base):
    """[summary]
    """

    __tablename__ = "players"
    discord_id = Column(BIGINT, primary_key=True)
    name = Column(String)
    guild_id = Column(BIGINT, ForeignKey("guilds.discord_id"))
    hero_instances = relationship("HeroInstance")

    def __repr__(self) -> str:
        """[summary]

        Returns:
            str: [description]
        """
        return f"Player<discord_id={self.discord_id}, name={self.name}>"
