
from sqlalchemy import Column, BIGINT, String
from sqlalchemy.orm import relationship

from albedo_bot.database.schema.base import base


class Guild(base):
    """[summary]
    """

    __tablename__ = "guilds"
    discord_id = Column(BIGINT, primary_key=True)
    name = Column(String)
    players = relationship("Player")

    def __repr__(self) -> str:
        """[summary]

        Returns:
            str: [description]
        """
        return f"<{self.discord_id}, {self.name}>"
