from pathlib import Path
from sqlalchemy import Column, String, Integer, ForeignKey

from albedo_bot.database.schema.base import base
from albedo_bot.cogs.utils.mixins.database_mixin import DatabaseMixin


class HeroPortrait(base, DatabaseMixin):
    """
    A hero image/portrait that is associated with a hero
    """

    __tablename__ = "hero_portraits"
    id = Column(Integer, ForeignKey("heroes.id"), primary_key=True)
    image_index = Column(Integer, primary_key=True)
    required = Column(Integer, primary_key=True)
    image_directory = Column(String)
    image_name = Column(String)

    def full_path(self):
        """
        Return the full file path as a Path object
        """

        return Path(self.image_directory, self.image_name)
