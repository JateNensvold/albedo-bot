from sqlalchemy import Column, ForeignKey, String, Integer, Text

from albedo_bot.database.schema.base import base


class HeroSignatureItem(base):
    """_summary_

    Args:
        Base (_type_): _description_
    """
    __tablename__ = "hero_signature_item"
    id = Column(Integer, ForeignKey("heroes.id"), primary_key=True)
    si_name = Column(String)
    image = Column(String)
    description = Column(Text)

    def __repr__(self) -> str:
        """[summary]

        Returns:
            str: [description]
        """
        return f"HeroSI<{self.id}, {self.si_name}>"


class HeroSignatureItemUpgrade(base):
    """_summary_

    Args:
        Base (_type_): _description_
    """
    __tablename__ = "hero_signature_item_upgrade"
    id = Column(Integer, ForeignKey("heroes.id"), primary_key=True)
    description = Column(Text)
    si_level = Column(Integer, primary_key=True)

    def __repr__(self) -> str:
        """[summary]

        Returns:
            str: [description]
        """
        return f"HeroSIUpgrade<{self.id}, {self.si_level}>"
