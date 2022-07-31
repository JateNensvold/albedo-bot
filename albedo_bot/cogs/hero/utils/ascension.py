
from typing import Union

from discord.ext import commands

from albedo_bot.database.schema.hero import (AscensionValues, Hero)
from albedo_bot.database.schema.hero.hero import HeroAscensionEnum
from albedo_bot.cogs.hero.utils.hero_value_mixin import HeroValueMixin

ASCENSION_VALUE_RANGE: list[tuple[str, int]] = AscensionValues.tuple_list()
ASCENDED_MAX_VALUE: dict[str, AscensionValues] = {
    ascension_type: AscensionValues[
        "A5"] for ascension_type in HeroAscensionEnum.list()}
ASCENDED_MAX_VALUE[HeroAscensionEnum.legendary] = AscensionValues["L+"]


class AscensionValue(HeroValueMixin):
    """_summary_

    Args:
        commands (_type_): _description_
    """

    def __init__(self, ascension_value: AscensionValues = None, hero=None, auto_detect: bool = True):
        """_summary_

        Args:
            ascension_value (str, optional): _description_. Defaults to None.
            hero (_type_, optional): _description_. Defaults to None.
            auto_detect (bool, optional): _description_. Defaults to True.
        """
        self.ascension_value = ascension_value
        self.hero = hero
        self.auto_detect = auto_detect

    def init(self, argument: str, ctx: commands.Context, hero: Hero = None):
        """
        If no hero is given then `auto_detect` determines if automatic
            hero_detection should be attempted

        Args:
            ctx (commands.Context): _description_
        """
        self.hero = None

        if hero:
            self.hero = hero
        elif self.auto_detect:
            self.hero = self.find_hero(ctx)

        self.ascension_value = self.check_ascension(argument, self.hero)

    @classmethod
    def check_ascension(cls, argument: Union[int, str], hero: Hero) -> AscensionValues:
        """
        Check if the `argument` provided is a valid ascension for `hero` throws
            BadArgument exception if the `argument` is invalid/out of bounds

        Args:
            argument (Union[str, int]): _description_
        """

        exception_string = (f"Invalid Ascension value given `{argument}`, "
                            "use one of the following values "
                            f"`{ASCENSION_VALUE_RANGE}`")

        try:
            ascension_value = int(argument)
            valid_ascension = AscensionValues(ascension_value)
        except ValueError as _exception:
            try:
                valid_ascension = AscensionValues[argument]
            except KeyError as exception:
                raise commands.BadArgument(exception_string) from exception

        if (valid_ascension.value > ASCENDED_MAX_VALUE[
                hero.ascension_tier].value):
            raise commands.BadArgument(exception_string)
        return valid_ascension

    @classmethod
    def ascension_range(cls, hero: Hero):
        """_summary_
        """

        return (AscensionValues(0), ASCENDED_MAX_VALUE[hero.ascension_tier])
