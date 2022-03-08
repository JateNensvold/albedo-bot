from sqlalchemy import Column, ForeignKey, String, Integer, Text

from albedo_bot.schema.base import Base


class HeroSignatureItem(Base):
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


class HeroSignatureItemUpgrade(Base):
    """_summary_

    Args:
        Base (_type_): _description_
    """
    __tablename__ = "hero_signature_item_upgrade"
    id = Column(Integer, ForeignKey("heroes.id"), primary_key=True)
    si_name = Column(String, ForeignKey(
        "hero_signature_item.name"))
    description = Column(Text)
    si_level = Column(Integer, primary_key=True)

    def __repr__(self) -> str:
        """[summary]

        Returns:
            str: [description]
        """
        return f"HeroSIUpgrade<{self.id}, {self.si_name}, {self.si_level}>"
