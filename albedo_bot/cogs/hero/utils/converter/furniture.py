
from typing import Union
from albedo_bot.cogs.hero.utils.converter.hero_value_mixin import HeroValueMixin
from albedo_bot.database.schema.hero import Hero
from albedo_bot.database.schema.hero.hero import HeroFactionEnum
from discord.ext import commands

FACTION_MAX_FURNITURE = {
    faction: 36 for faction in HeroFactionEnum.list()}


class FurnitureValue(HeroValueMixin):
    """_summary_

    Args:
        commands (_type_): _description_
    """

    def __init__(self, furniture_value: int = None, hero: Hero = None,
                 auto_detect: bool = True):
        """_summary_

        Args:
            si_value (int, optional): _description_. Defaults to None.
            hero (Hero, optional): _description_. Defaults to None.
            auto_detect (bool, optional): _description_. Defaults to None.
        """

        self.furniture_value = furniture_value
        self.hero = hero
        self.auto_detect = auto_detect

    async def init(self, argument: Union[int, str], ctx: commands.Context,
             hero: Hero = None):
        """
        Initialize the arguments needed to create a FurnitureValue

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        """
        self.hero = None

        if hero:
            self.hero = hero
        elif self.auto_detect:
            self.hero = self.find_hero(ctx)

        self.furniture_value = self.check_furniture(self.hero, argument)

    @classmethod
    def check_furniture(cls, hero: Hero, furniture: int):
        """_summary_

        Args:
            hero (Hero): _description_
            furniture (int): _description_

        Returns:
            _type_: _description_
        """

        furniture = int(furniture)

        if (furniture < 0 or furniture > FACTION_MAX_FURNITURE[
                hero.hero_faction]):
            raise commands.BadArgument(
                f"Invalid furniture value given `{furniture}` for {hero.name}, "
                "enter a value in the following range "
                f"`{cls.furniture_range(hero)}`")
        return furniture

    @classmethod
    def furniture_range(cls, hero: Hero):
        """_summary_

        Args:
            hero (_type_): _description_
        """

        return (0, FACTION_MAX_FURNITURE[hero.hero_faction])
