from sqlalchemy import Column, ForeignKey, String, Integer, Text

from albedo_bot.database.schema.base import base


class HeroFurniture(base):
    """
    A database representation of Heroes furniture
    """

    __tablename__ = "hero_furniture"
    id = Column(Integer, ForeignKey("heroes.id"),
                primary_key=True, nullable=False)
    furniture_name = Column(String)
    image = Column(String)

    def __repr__(self) -> str:
        """
        A quick str representation of a HeroFurniture

        Returns:
            str: str representation of a HeroFurniture
        """
        return f"HeroFurniture<{self.id}, {self.furniture_name}>"


class HeroFurnitureUpgrade(base):
    """
    A database representation of a Heroes furniture upgrades
    """

    __tablename__ = "hero_furniture_upgrade"
    id = Column(Integer, ForeignKey("heroes.id"), primary_key=True)
    description = Column(Text)
    furniture_unlock = Column(Integer, primary_key=True)

    def __repr__(self) -> str:
        """
        A quick str representation of a HeroFurnitureUpgrade

        Returns:
            str: str representation of a HeroFurnitureUpgrade
        """
        return f"HeroFurnitureUpgrade<{self.id}, {self.furniture_unlock}>"
