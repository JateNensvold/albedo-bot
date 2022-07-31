

from typing import Union
from albedo_bot.cogs.hero.utils.hero_value_mixin import HeroValueMixin
from albedo_bot.database.schema.hero import Hero
from albedo_bot.database.schema.hero.hero import HeroFactionEnum

from discord.ext import commands

FACTION_MAX_ENGRAVING = {
    faction: 80 for faction in HeroFactionEnum.list()}
FACTION_MAX_ENGRAVING[HeroFactionEnum.Celestial] = 100
FACTION_MAX_ENGRAVING[HeroFactionEnum.Hypogean] = 100
FACTION_MAX_ENGRAVING[HeroFactionEnum.Dimensional] = 100


class EngravingValue(HeroValueMixin):
    """_summary_

    Args:
        HeroValueMixin (_type_): _description_
    """

    def __init__(self, engraving_value: int = None, hero: Hero = None,
                 auto_detect: bool = True):
        """_summary_

        Args:
            engraving_value (int, optional): _description_. Defaults to None.
            hero (Hero, optional): _description_. Defaults to None.
            auto_detect (bool, optional): _description_. Defaults to None.
        """

        self.engraving_value = engraving_value
        self.hero = hero
        self.auto_detect = auto_detect

    def init(self, argument: Union[int, str], ctx: commands.Context, hero: Hero = None):
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

        self.engraving_value = self.check_engraving(self.hero, argument)

    @classmethod
    def check_engraving(cls, hero: Hero, engraving: int):
        """_summary_

        Args:
            hero (Hero): _description_
            engraving (int): _description_

        Returns:
            _type_: _description_
        """
        engraving = int(engraving)
        if engraving < 0 or engraving > FACTION_MAX_ENGRAVING[hero.hero_faction]:
            raise commands.BadArgument(
                f"Invalid engraving value given `{engraving}` for {hero.name}, "
                "enter a value in the following range "
                f"`{cls.engraving_range(hero)}`")
        return engraving

    @classmethod
    def engraving_range(cls, hero: Hero):
        """_summary_

        Args:
            hero (_type_): _description_
        """

        return (0, FACTION_MAX_ENGRAVING[hero.hero_faction])
