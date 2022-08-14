

from sqlalchemy import Column, ForeignKey, BIGINT, Integer
from sqlalchemy import Enum as SQLEnum
from albedo_bot.database.schema.base import base
from albedo_bot.utils.enums.elder_tree_enum import ElderTreeTypesEnum


class PlayerElderTree(base):
    """
    AlbedoBot player's ElderTree Schema
    """

    __tablename__ = "player_elder_tree"
    player_id = Column(BIGINT, ForeignKey(
        "players.discord_id"), primary_key=True)
    hero_id = Column(Integer, ForeignKey("heroes.id"), primary_key=True)
    tree_branch = Column(SQLEnum(ElderTreeTypesEnum), primary_key=True)
