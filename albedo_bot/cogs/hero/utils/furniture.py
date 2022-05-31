
from albedo_bot.database.schema.hero import Hero
from albedo_bot.database.schema.hero.hero import faction_values
from discord.ext import commands

FACTION_MAX_FURNITURE = {faction: 36 for faction in faction_values}


def check_furniture(hero: Hero, furniture: int):
    """_summary_

    Args:
        hero (Hero): _description_
        furniture (int): _description_

    Returns:
        _type_: _description_
    """
    if furniture < 0 or furniture > FACTION_MAX_FURNITURE[hero.hero_faction]:
        raise commands.BadArgument(
            f"Invalid furniture value given `{furniture}` for {hero.name}, "
            "enter a value in the following range "
            f"`{furniture_range(hero)}`")


def furniture_range(hero: Hero):
    """_summary_

    Args:
        hero (_type_): _description_
    """

    return (0, FACTION_MAX_FURNITURE[hero.hero_faction])
