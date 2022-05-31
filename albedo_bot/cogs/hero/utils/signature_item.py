
from albedo_bot.database.schema.hero.hero import faction_values, Hero
from discord.ext import commands

FACTION_MAX_SI = {faction: 30 for faction in faction_values}
FACTION_MAX_SI[faction_values.celestial] = 40
FACTION_MAX_SI[faction_values.hypogean] = 40
FACTION_MAX_SI[faction_values.dimensional] = 40


def check_signature_item(hero: Hero, signature_item: int):
    """_summary_

    Args:
        hero (Hero): _description_
        signature_item (int): _description_

    Returns:
        _type_: _description_
    """
    if signature_item < 0 or signature_item > FACTION_MAX_SI[hero.hero_faction]:
        raise commands.BadArgument(
            f"Invalid SI value value given `{signature_item}` for {hero.name}, "
            "enter a value in the following range "
            f"`{signature_item_range(hero)}`")


def signature_item_range(hero: Hero):
    """_summary_

    Args:
        hero (_type_): _description_
    """

    return (0, FACTION_MAX_SI[hero.hero_faction])
