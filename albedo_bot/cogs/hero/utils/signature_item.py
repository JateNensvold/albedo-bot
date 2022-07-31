
from typing import Union
from albedo_bot.cogs.hero.utils.hero_value_mixin import HeroValueMixin
from albedo_bot.database.schema.hero.hero import HeroFactionEnum, Hero
from discord.ext import commands

FACTION_MAX_SI = {faction: 30 for faction in HeroFactionEnum.list()}
FACTION_MAX_SI[HeroFactionEnum.Celestial] = 40
FACTION_MAX_SI[HeroFactionEnum.Hypogean] = 40
FACTION_MAX_SI[HeroFactionEnum.Dimensional] = 40


class SignatureItemValue(HeroValueMixin):
    """_summary_

    Args:
        commands (_type_): _description_
    """

    def __init__(self, si_value: int = None, hero: Hero = None,
                 auto_detect: bool = True):
        """_summary_

        Args:
            si_value (int, optional): _description_. Defaults to None.
            hero (Hero, optional): _description_. Defaults to None.
            auto_detect (bool, optional): _description_. Defaults to None.
        """

        self.si_value = si_value
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

        self.si_value = self.check_signature_item(self.hero, argument)

    @classmethod
    def check_signature_item(cls, hero: Hero, signature_item: int):
        """_summary_

        Args:
            hero (Hero): _description_
            signature_item (int): _description_

        Returns:
            _type_: _description_
        """
        signature_item = int(signature_item)

        if (signature_item < 0 or signature_item > FACTION_MAX_SI[
                hero.hero_faction]):
            raise commands.BadArgument(
                f"Invalid SI value value given `{signature_item}` for "
                f"{hero.name}, enter a value in the following range "
                f"`{cls.signature_item_range(hero)}`")
        return signature_item

    @classmethod
    def signature_item_range(cls, hero: Hero):
        """_summary_

        Args:
            hero (_type_): _description_
        """

        return (0, FACTION_MAX_SI[hero.hero_faction])
