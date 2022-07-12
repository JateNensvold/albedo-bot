import os
from typing import List, NamedTuple, Union, TYPE_CHECKING
from enum import Enum

from sqlalchemy import Column, ForeignKey, Integer, BIGINT
from sqlalchemy import Enum as SQLEnum

from albedo_bot.cogs.utils.mixins.database_mixin import DatabaseMixin
from albedo_bot.cogs.utils.mixins.emoji_mixin import EmojiMixin
from albedo_bot.database.schema.base import base
from albedo_bot.database.schema.hero import Hero
from albedo_bot.utils.emoji import busts_in_silhouette

if TYPE_CHECKING:
    from albedo_bot.bot import AlbedoBot

ascension_values = {"None": 0,
                    "E": 1,
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
    signature_level: int
    furniture_level: int
    ascension_level: AscensionValues
    engraving_level: int

    @classmethod
    async def from_hero_instance(cls, db_handle: DatabaseMixin,
                                 hero_instances: list["HeroInstance"]):
        """_summary_

        Args:
            hero_instance (HeroInstance): _description_

        Returns:
            _type_: _description_
        """

        hero_instance_tuple_list: list[HeroInstanceTuple] = []

        # Convert hero_instances into a list if only a single hero_instance
        #   was provided
        if not isinstance(hero_instances, list):
            hero_instances = [hero_instances]

        for hero_instance in hero_instances:
            hero_select = db_handle.db_select(Hero).where(
                Hero.id == hero_instance.hero_id)

            hero_object = await db_handle.db_execute(hero_select).first()
            hero_instance_tuple_list.append(
                HeroInstanceTuple(hero_object.name, hero_instance.hero_id,
                                  hero_instance.signature_level,
                                  hero_instance.furniture_level,
                                  hero_instance.ascension_level,
                                  hero_instance.engraving_level))

        return hero_instance_tuple_list


class HeroList(DatabaseMixin, EmojiMixin):
    """_summary_
    """

    def __init__(self, bot: "AlbedoBot", heroes: List[HeroInstanceTuple]):
        """_summary_

        Args:
            heroes (List[HeroInstanceTuple]): _description_
        """
        # Set self.bot for DatabaseMixin
        self.bot = bot
        self.longest_name = len(
            max((*[hero.hero_name for hero in heroes], ""), key=len))
        self.heroes = heroes

    async def format_heroes(self):
        """_summary_

         Returns:
             _type_: _description_
        """
        formated_heroes = []

        formated_heroes.append(
            f"{busts_in_silhouette} `{'Heroes': <{self.longest_name}} ASC SI FI ENGRAVING`")

        for hero_tuple in self.heroes:

            hero_select = self.db_select(Hero).where(
                Hero.id == hero_tuple.hero_id)
            hero_result = await self.db_execute(hero_select).first()

            portrait_name, _portrait_extension = os.path.splitext(
                os.path.basename(hero_result.hero_portrait))
            formated_heroes.append(
                f"{str(self.get_emoji(portrait_name))} "
                f"`{hero_tuple.hero_name: <{self.longest_name}} "
                f"{hero_tuple.ascension_level.name: <{3}} "
                f"{hero_tuple.signature_level: <2} "
                f"{hero_tuple.furniture_level: <2} "
                f"{hero_tuple.engraving_level}`")
        message = "\n".join(formated_heroes)
        output = f"{message}"
        return output

    # def generate_embed(self):
    #     """_summary_

    #     Returns:
    #         _type_: _description_
    #     """
    #     blank_field = "\u200b"

    #     embed_object = Embed(
    #         title="Title", description="Description", color=0xffbf00)
    #     # embed_object.add_field(name="Heroes", value=blank_field, inline=True)
    #     header_string = f"{'Heroes': <{self.longest_name}} ASC SI FI ENGRAVING"
    #     embed_object.add_field(
    #         name=header_string, value=blank_field,  inline=False)

    #     for hero_tuple in self.heroes:
    #         hero_object: Hero = GV.session.query(Hero).filter_by(
    #             id=hero_tuple.hero_id).first()
    #         portrait_name, _portrait_ext = os.path.splitext(
    #             os.path.basename(hero_object.hero_portrait))
    #         hero_string = (f"{str(get_emoji(portrait_name))} "
    #                        f"`{hero_tuple.hero_name: <{self.longest_name}} "
    #                        f"{hero_tuple.ascension: <{3}} "
    #                        f"{hero_tuple.si: <2} "
    #                        f"{hero_tuple.fi: <2} "
    #                        f"{hero_tuple.engraving}`")
    #         # hero_string.replace(" ", "\u1CBC\u1CBC")
    #         # hero_string = re.sub(r"\S", "\u1CBC", hero_string)
    #         print(hero_string)
    #         embed_object.add_field(
    #             name=hero_string, value=hero_string, inline=False)

    #     return embed_object

    def __str__(self):
        """_summary_
        """
        return f"HeroList<{len(self.heroes)} heroes long>"

    async def async_str(self):
        """_summary_
        """
        output = await self.format_heroes()
        return output


class HeroInstance(base):
    """[summary]

    Args:
        base ([type]): [description]

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

    def __init__(self, hero_id, player_id, signature_level=0,
                 furniture_level=0, ascension_level=AscensionValues(0),
                 engraving_level=0):
        self.hero_id = hero_id
        self.player_id = player_id
        self.signature_level = int(signature_level)
        self.furniture_level = int(furniture_level)
        self.ascension_level = ascension_level
        self.engraving_level = int(engraving_level)

    def __repr__(self) -> str:
        """[summary]

        Returns:
            str: [description]
        """
        return f"HeroInstance<hero_id={self.hero_id}, player_id={self.player_id}>"

    def __str__(self) -> str:
        """_summary_

        Returns:
            str: _description_
        """
        return (f"{self.hero_id} {self.ascension_level} "
                f"{self.signature_level}{self.furniture_level} "
                f"{self.engraving_level}")

    def update(self, signature_level: Union[int, str],
               furniture: Union[int, str], ascension: str,
               engraving: Union[int, str]):
        """_summary_

        Args:
            signature_level (int): _description_
            furniture (int): _description_
            ascension (str): _description_
            engraving (int): _description_

        Returns:
            _type_: _description_
        """
        updated = False
        signature_level = int(signature_level)
        furniture = int(furniture)
        engraving = int(engraving)

        if signature_level > self.signature_level:
            updated = True
            self.signature_level = int(signature_level)
        if furniture > self.furniture_level:
            updated = True
            self.furniture_level = int(furniture)
        if AscensionValues[ascension].value > self.ascension_level.value:
            updated = True
            self.ascension_level = AscensionValues[ascension]
        if engraving > self.engraving_level:
            updated = True
            self.engraving_level = int(engraving)

        return updated
