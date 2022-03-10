
from typing import List, NamedTuple

from sqlalchemy import Column, ForeignKey, Integer, BIGINT
from sqlalchemy import Enum

from albedo_bot.schema.base import Base

ascension_values = ("E",
                    "E+",
                    "L",
                    "L+",
                    "M",
                    "M+",
                    "A",
                    "A1",
                    "A2",
                    "A3",
                    "A4",
                    "A5")
ASCENSION_ENUM = Enum(*ascension_values, name="ascension_enum")


class HeroInstanceTuple(NamedTuple):
    """_summary_

    Args:
        namedtuple (_type_): _description_

    Returns:
        _type_: _description_
    """
    hero_name: str
    hero_id: int
    si: int
    fi: int
    ascension: str
    engraving: int


class HeroList:
    """_summary_
    """

    def __init__(self, heroes: List[HeroInstanceTuple]):
        """_summary_

        Args:
            heroes (List[HeroInstanceTuple]): _description_
        """
        self.longest_name = len(max((heroes, ""), key=len))
        self.heroes = heroes

    def format_heroes(self):
        """_summary_

         Returns:
             _type_: _description_
        """
        formated_heroes = []

        formated_heroes.append(
            f"{'Heroes': <{self.longest_name}} ASC SI FI ENGRAVING")
        for hero_tuple in self.heroes:
            formated_heroes.append(
                f"{hero_tuple.hero_name: <{self.longest_name}} "
                f"{hero_tuple.ascension: <{3}} "
                f"{hero_tuple.si: <2} "
                f"{hero_tuple.fi: <2} "
                f"{hero_tuple.engraving}")
        message = "\n".join(formated_heroes)
        output = f"```css\n{message}\n```"
        return output

    def __str__(self):
        """_summary_
        """
        return self.format_heroes()


class HeroInstance(Base):
    """[summary]

    Args:
        Base ([type]): [description]

    Returns:
        [type]: [description]
    """

    __tablename__ = "hero_instances"
    hero_id = Column(Integer, ForeignKey("heroes.id"), primary_key=True)
    player_id = Column(BIGINT, ForeignKey(
        "players.discord_id"), primary_key=True)
    signature_level = Column(Integer)
    furniture_level = Column(Integer)
    ascension_level = Column(ASCENSION_ENUM)
    engraving_level = Column(Integer)

    def __repr__(self) -> str:
        """[summary]

        Returns:
            str: [description]
        """
        return f"HeroInstance<{self.hero_id}, {self.player_id}>"

    def __str__(self) -> str:
        """_summary_

        Returns:
            str: _description_
        """
        return (f"{self.hero_id} {self.ascension_level} "
                f"{self.signature_level}{self.furniture_level} "
                f"{self.engraving_level}")
