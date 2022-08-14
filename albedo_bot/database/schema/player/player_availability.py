
from sqlalchemy import Column, BIGINT, ForeignKey
from sqlalchemy import Enum as SQLEnum


from albedo_bot.database.schema.base import base
from albedo_bot.utils.enums.availability_enum import AVAILABILITY_ENUM


class PlayerAvailability(base):
    """
    A table for keeping track of when players are available to player AFK Arena
    """

    __tablename__ = "player_availability"
    player_id = Column(BIGINT, ForeignKey(
        "players.discord_id"), primary_key=True)
    availability = Column(
        SQLEnum(AVAILABILITY_ENUM), primary_key=True)
