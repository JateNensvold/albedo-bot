

from abc import abstractmethod
from typing import Any,  TYPE_CHECKING
from albedo_bot.cogs.hero.utils.converter import converter_util
from albedo_bot.utils.errors import ConversionError

from discord.ext import commands

from albedo_bot.database.schema.hero.hero import Hero

if TYPE_CHECKING:
    from albedo_bot.bot import AlbedoBot


class HeroValueMixin(commands.Converter):
    """_summary_
    """

    @abstractmethod
    async def init(self, argument: Any, ctx: commands.Context,
                   hero: Hero = None):
        """
        Initialize the argument being set by the converter
        """

    async def convert(self, ctx: commands.Context, argument: str):
        """_summary_

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            argument (Union[str, int]): _description_

        Raises:
            BadArgument: _description_

        Returns:
            _type_: _description_
        """

        self.bot: "AlbedoBot" = ctx.bot

        await self.init(argument, ctx)
        return self

    def find_hero(self, ctx: commands.Context):
        """
        This command will raise an error when a Hero is unable to be found in
            the ctx arguments

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        """

        hero_object: Hero = None

        for message_arg in ctx.args:
            hero_object = converter_util.is_hero(message_arg)
            if hero_object:
                break

        if hero_object is None:
            raise ConversionError(
                "Unable to detect a hero argument in this commands discord context")

        return hero_object
