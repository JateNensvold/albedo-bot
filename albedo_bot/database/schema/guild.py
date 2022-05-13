
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

    def __repr__(self):
        """[summary]

        Returns:
            str: [description]
        """
        return f"Guild<discord_id={self.discord_id}, name='{self.name}'>"

    def __str__(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.guild_mention_no_ping

    @property
    def guild_mention_no_ping(self):
        """_summary_
        """
        return f"<@&{self.discord_id}>"
