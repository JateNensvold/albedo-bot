from discord.ext import commands
from albedo_bot.database.schema.hero import AscensionValues

ASCENSION_VALUE_RANGE: list[tuple[str, int]] = [(value.name, value.value)
                                                for value in AscensionValues]


def check_ascension(argument: int) -> AscensionValues:
    """_summary_

    Args:
        ctx (commands.Context): _description_
    argument (Union[str, int]): _description_
    """

    exception_string = (f"Invalid Ascension value given `{argument}`, "
                        "use one of the following values `{ascension_range()}`")

    try:
        ascension_value = int(argument)
        return AscensionValues(ascension_value)
    except ValueError as _exception:
        try:
            return AscensionValues[argument]
        except KeyError as exception:
            raise commands.BadArgument(exception_string) from exception


def ascension_range():
    """_summary_

    """

    return ASCENSION_VALUE_RANGE
