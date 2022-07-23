
from albedo_bot.database.schema.hero.hero import HeroClassEnum
from discord.ext import commands


class HeroClass(commands.Converter):
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
            return HeroClassEnum(argument)
        except Exception as exception:
            raise commands.BadArgument(
                (f"Invalid Class given `{argument}`, class must be one of "
                 f"the following `{HeroClassEnum.list()}`")) from exception
