
from typing import TYPE_CHECKING, Union
from albedo_bot.cogs.hero.utils.converter.hero_value_mixin import HeroValueMixin
from albedo_bot.database.schema.hero.hero import Hero
from discord.ext import commands

from albedo_bot.database.schema.checklist import Checklist
from albedo_bot.cogs.utils.mixins.database_mixin import DatabaseMixin


if TYPE_CHECKING:
    from albedo_bot.bot import AlbedoBot


class ChecklistValue(HeroValueMixin, DatabaseMixin):
    """
    A wrapper class around Checklist to do argument conversion into
    Checklist objects
    """

    def __init__(self, checklist: Checklist = None):
        """
        Initialize all the values that the converter sets while converting

        Args:
            si_value (int, optional): _description_. Defaults to None.
            hero (Hero, optional): _description_. Defaults to None.
            auto_detect (bool, optional): _description_. Defaults to None.
        """

        self.checklist = checklist

    async def init(self, argument: Union[int, str], ctx: commands.Context,
                   hero: Hero = None):
        """
        Initialize the arguments needed to create a ChecklistValue

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        """

        self.checklist = await self.check(ctx, argument)

    async def check(self, ctx: commands.Context, argument: str):
        """
        Convert an argument into a checklist

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
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
