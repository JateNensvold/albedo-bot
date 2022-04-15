

from typing import Union
from albedo_bot.database.schema.hero import AscensionValues

ASCENSION_VALUE_RANGE = [(value.name, value.value)
                         for value in AscensionValues]


def valid_ascension(ascension_value: Union[int, str]):
    """_summary_

    Args:
        ascension_value (Union[int, str]): _description_
    """

    try:
        ascension_value = int(ascension_value)
        AscensionValues(ascension_value)
    except ValueError as _exception:
        try:
            ascension_value = AscensionValues[ascension_value]
        except KeyError as _exception:
            return False
    return True


def ascension_range():
    """_summary_

    """

    return ASCENSION_VALUE_RANGE
