
from albedo_bot.database.schema.hero.hero import HeroTypeEnum
from discord.ext import commands


class HeroType(commands.Converter):
    """_summary_

    Args:
        Converter (_type_): _description_
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
        try:
            return HeroTypeEnum(argument)
        except Exception as exception:
            raise commands.BadArgument(
                (f"Invalid hero type given `{argument}`, hero type must be one "
                 f"of the following `{HeroTypeEnum.v_list()}`")) from exception
