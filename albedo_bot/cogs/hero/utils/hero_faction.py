
from albedo_bot.database.schema.hero.hero import HeroFactionEnum
from discord.ext import commands


class HeroFaction(commands.Converter):
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
            return HeroFactionEnum(argument)
        except Exception as exception:
            raise commands.BadArgument(
                (f"Invalid Faction given `{argument}`, factions must be one of "
                 f"the following `{HeroFactionEnum.list()}`")) from exception
