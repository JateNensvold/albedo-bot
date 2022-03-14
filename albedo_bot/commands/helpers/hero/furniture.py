
from albedo_bot.schema.hero.hero import faction_values
from albedo_bot.schema.hero import Hero


FACTION_MAX_FURNITURE = {faction: 36 for faction in faction_values}


def valid_furniture(hero: Hero, furniture: int):
    """_summary_

    Args:
        hero (Hero): _description_
        furniture (int): _description_

    Returns:
        _type_: _description_
    """
    if furniture < 0 or furniture > FACTION_MAX_FURNITURE[hero.hero_faction]:
        return False
    return True


def furniture_range(hero: Hero):
    """_summary_

    Args:
        hero (_type_): _description_
    """

    return (0, FACTION_MAX_FURNITURE[hero.hero_faction])