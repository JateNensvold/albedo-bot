

from discord.ext import commands
from typing import Union
from albedo_bot.database.schema.hero import AscensionValues
from albedo_bot.utils.errors import ConversionError

ASCENSION_VALUE_RANGE = [(value.name, value.value)
                         for value in AscensionValues]


def check_ascension(argument: int) -> AscensionValues:
    """_summary_

    Args:
        ctx (commands.Context): _description_
    argument (Union[str, int]): _description_
    """

    excpetion_string = (f"Invalid Ascension value given `{argument}`, use one of the "
                        f"following values `{ascension_range()}`")

    try:
        ascension_value = int(argument)
        return AscensionValues(ascension_value)
    except ValueError as _exception:
        try:
            return AscensionValues[argument]
        except KeyError as exception:
            raise commands.BadArgument(excpetion_string) from exception


# def valid_ascension(ascension_value: Union[int, str]):
#     """_summary_

#     Args:
#         ascension_value (Union[int, str]): _description_
#     """

#     try:
#         ascension_value = int(ascension_value)
#         AscensionValues(ascension_value)
#     except ValueError as _exception:
#         try:
#             ascension_value = AscensionValues[ascension_value]
#         except KeyError as _exception:
#             return False
#     return True


def ascension_range():
    """_summary_

    """

    return ASCENSION_VALUE_RANGE
