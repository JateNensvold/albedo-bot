

from albedo_bot.database.schema.hero import Hero
from albedo_bot.database.schema.hero.hero import HeroFactionEnum

from discord.ext import commands

FACTION_MAX_ENGRAVING = {faction: 80 for faction in HeroFactionEnum.list()}
FACTION_MAX_ENGRAVING[HeroFactionEnum.Celestial] = 100
FACTION_MAX_ENGRAVING[HeroFactionEnum.Hypogean] = 100
FACTION_MAX_ENGRAVING[HeroFactionEnum.Dimensional] = 100


def check_engraving(hero: Hero, engraving: int):
    """_summary_

    Args:
        hero (Hero): _description_
        engraving (int): _description_

    Returns:
        _type_: _description_
    """
    if engraving < 0 or engraving > FACTION_MAX_ENGRAVING[hero.hero_faction]:
        raise commands.BadArgument(
            f"Invalid engraving value given `{engraving}` for {hero.name}, "
            "enter a value in the following range "
            f"`{engraving_range(hero)}`")


def engraving_range(hero: Hero):
    """_summary_

    Args:
        hero (_type_): _description_
    """

    return (0, FACTION_MAX_ENGRAVING[hero.hero_faction])
