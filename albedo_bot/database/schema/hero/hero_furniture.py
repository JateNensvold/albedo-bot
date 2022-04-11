from sqlalchemy import Column, ForeignKey, String, Integer, Text, null

from albedo_bot.database.schema.base import base


class HeroFurniture(base):
    """_summary_

    Args:
        base (_type_): _description_
    """

    __tablename__ = "hero_furniture"
    id = Column(Integer, ForeignKey("heroes.id"),
                     primary_key=True, nullable=False)
    furniture_name = Column(String)
    image = Column(String)

    def __repr__(self) -> str:
        """[summary]

        Returns:
            str: [description]
        """
        return f"HeroFurniture<{self.id}, {self.furniture_name}>"


class HeroFurnitureUpgrade(base):
    """_summary_

    Args:
        base (_type_): _description_
    """

    __tablename__ = "hero_furniture_upgrade"
    id = Column(Integer, ForeignKey("heroes.id"), primary_key=True)
    description = Column(Text)
    furniture_unlock = Column(Integer, primary_key=True)

    def __repr__(self) -> str:
        """[summary]

        Returns:
            str: [description]
        """
        return f"HeroFurnitureUpgrade<{self.id}, {self.furniture_unlock}>"
