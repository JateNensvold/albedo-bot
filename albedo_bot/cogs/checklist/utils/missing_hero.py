
from typing import NamedTuple, Union, TYPE_CHECKING


if TYPE_CHECKING:
    from albedo_bot.database.schema.hero.hero_instance import HeroInstanceData


class MissingHero(NamedTuple):
    """
    Wrapper around the requirement for a hero, and the hero instance that
        was provided

    hero_instance can be None
    """

    checklist_hero: "HeroInstanceData"
    hero_instance: Union["HeroInstanceData", None]
