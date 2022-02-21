
from albedo_bot.schema.base import Base

from sqlalchemy import Column, ForeignKey, Integer, BIGINT


class HeroInstance(Base):
    """[summary]

    Args:
        Base ([type]): [description]

    Returns:
        [type]: [description]
    """

    __tablename__ = "hero_instances"
    hero_id = Column(Integer, ForeignKey("hero.id"), primary_key=True)
    player_id = Column(BIGINT, ForeignKey(
        "player.discord_id"), primary_key=True)
    signature_level = Column(Integer)
    furniture_level = Column(Integer)
    ascension_level = Column(Integer)
    engraving_level = Column(Integer)

    def __repr__(self) -> str:
        """[summary]

        Returns:
            str: [description]
        """
        return f"{self.guild_id}, {self.name}, {self.mention}"
