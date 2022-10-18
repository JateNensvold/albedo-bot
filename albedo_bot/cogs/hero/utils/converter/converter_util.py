

from typing import Any
from albedo_bot.database.schema.hero.abstract_hero_container import (
    AbstractHeroContainer)
from albedo_bot.database.schema.hero.hero import Hero


def is_hero(argument: Hero | AbstractHeroContainer | Any):
    """
    A conversion utility method that can be used to 

    Args:
        argument (HeroLike object): an object to 

    Returns:
        (Hero | None): a Hero when a `Hero` can be detected from argument, 
            None Otherwise 
    """
    if isinstance(argument, AbstractHeroContainer):
        return argument.hero
    elif isinstance(argument, Hero):
        return argument
