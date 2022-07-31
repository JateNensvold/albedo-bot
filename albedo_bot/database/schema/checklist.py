
from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, String, Integer, BIGINT
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SQLEnum
from discord.ext import commands

from albedo_bot.database.schema.base import base
from albedo_bot.cogs.utils.mixins.database_mixin import DatabaseMixin
from albedo_bot.database.schema.hero.hero_instance import AscensionValues

if TYPE_CHECKING:
    from albedo_bot.bot import AlbedoBot


class Checklist(base, commands.Converter, DatabaseMixin):
    """[summary]
    """

    __tablename__ = "checklists"
    name = Column(String, primary_key=True)
    description = Column(String)
    checklist_hero = relationship("ChecklistHero", cascade="all,delete")

    def __repr__(self) -> str:
        """[summary]

        Returns:
            str: [description]
        """
        return f"Checklist<{self.name}>"

    async def convert(self, ctx: commands.Context, argument: str):
        """_summary_

        Args:
            ctx (commands.Context): _description_
            argument (str): _description_

        Returns:
            _type_: _description_
        """
        self.bot: "AlbedoBot" = ctx.bot
        try:
            checklist_select = self.db_select(
                Checklist).where(Checklist.name == argument)
            checklist_object = await self.db_execute(checklist_select).first()
            if checklist_object is None:
                raise AttributeError
            return checklist_object
        except Exception as exception:
            raise commands.BadArgument(
                (f"Invalid checklist name given `{argument}`, checklist name "
                 f"must be shown by the `{self.bot.default_prefix}checklist "
                 "list` command")
            ) from exception


class ChecklistHero(base):
    """[summary]
    """

    __tablename__ = "checklist_heroes"
    checklist_name = Column(
        String, ForeignKey("checklists.name"), primary_key=True)
    hero_id = Column(BIGINT, ForeignKey("heroes.id"), primary_key=True)

    signature_level = Column(Integer)
    furniture_level = Column(Integer)
    ascension_level = Column(SQLEnum(AscensionValues, name="ascension_enum"))
    engraving_level = Column(Integer)

    def __repr__(self) -> str:
        """[summary]

        Returns:
            str: [description]
        """
        return f"ChecklistHero<{self.checklist_name}, {self.hero_id}>"
