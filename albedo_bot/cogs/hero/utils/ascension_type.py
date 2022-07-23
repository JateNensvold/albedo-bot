
from albedo_bot.database.schema.hero.hero import HeroAscensionEnum
from discord.ext import commands


class AscensionType(commands.Converter):
    """_summary_

    Args:
        Converter (_type_): _description_
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
        try:
            return HeroAscensionEnum(argument)
        except Exception as exception:
            raise commands.BadArgument(
                (f"Invalid ascension type given `{argument}`, ascension type "
                 f"must be one of the following `{HeroAscensionEnum.list()}`")
            ) from exception
