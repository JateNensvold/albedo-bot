
from albedo_bot.schema.hero.hero import faction_values
from albedo_bot.schema.hero import Hero


FACTION_MAX_SI = {faction: 30 for faction in faction_values}
FACTION_MAX_SI[faction_values.celestial] = 40
FACTION_MAX_SI[faction_values.hypogean] = 40
FACTION_MAX_SI[faction_values.dimensional] = 40


def valid_signature_item(hero: Hero, signature_item:int):
    """_summary_

    Args:
        hero (Hero): _description_
        signature_item (int): _description_

    Returns:
        _type_: _description_
    """
    if signature_item < 0 or signature_item > FACTION_MAX_SI[hero.hero_faction]:
        return False
    return True


def signature_item_range(hero: Hero):
    """_summary_

    Args:
        hero (_type_): _description_
    """

    return (0, FACTION_MAX_SI[hero.hero_faction])