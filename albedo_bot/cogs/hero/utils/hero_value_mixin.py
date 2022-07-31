

from abc import abstractmethod
from typing import Any

from discord.ext import commands

from albedo_bot.database.schema.hero.hero import Hero


class HeroValueMixin(commands.Converter):
    """_summary_
    """

    @abstractmethod
    def init(self, argument: Any, ctx: commands.Context, hero: Hero = None):
        """
        Initialize the argument being set by the converter
        """

    async def convert(self, ctx: commands.Context, argument: str):
        """_summary_

        Args:
            ctx (Context): _description_
            argument (Union[str, int]): _description_

        Raises:
            BadArgument: _description_

        Returns:
            _type_: _description_
        """

        self.init(argument, ctx)
        return self

    def find_hero(self, ctx: commands.Context):
        """
        This command will raise an error when a Hero is unable to be found in
            the ctx arguments

        Args:
            ctx (commands.Context): _description_
        """

        hero_object: Hero = None

        for message_arg in ctx.args:
            if isinstance(message_arg, Hero):
                hero_object = message_arg

        return hero_object
