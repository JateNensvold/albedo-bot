import re
from typing import List, NamedTuple
from enum import Enum

from sqlalchemy import Column, ForeignKey, Integer, BIGINT
from sqlalchemy import Enum as SQLEnum

from albedo_bot.schema.base import Base


ascension_values = {"E": 1,
                    "E+": 2,
                    "L": 3,
                    "L+": 4,
                    "M": 5,
                    "M+": 6,
                    "A": 7,
                    "A1": 8,
                    "A2": 9,
                    "A3": 10,
                    "A4": 11,
                    "A5": 12}

AscensionValues = Enum(value="AscensionValues", names=ascension_values)


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
    ascension: AscensionValues
    engraving: int


class HeroList:
    """_summary_
    """

    def __init__(self, heroes: List[HeroInstanceTuple]):
        """_summary_

        Args:
            heroes (List[HeroInstanceTuple]): _description_
        """
        self.longest_name = len(
            max((*[hero.hero_name for hero in heroes], ""), key=len))
        self.heroes = heroes

    def format_heroes(self):
        """_summary_

         Returns:
             _type_: _description_
        """
        formated_heroes = []

        formated_heroes.append(
            f"{'Heroes': <{self.longest_name}} ASC SI FI ENGRAVING")
        header_string = formated_heroes[0]

        dashed_string = re.sub(r"\S", "-", header_string)
        formated_heroes.append(dashed_string)
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
    ascension_level = Column(SQLEnum(AscensionValues, name="ascension_enum"))
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
