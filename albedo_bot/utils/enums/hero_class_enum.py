
from albedo_bot.cogs.utils.mixins.enum_mixin import StrEnum


class HeroClassEnum(StrEnum):
    """
    An enumeration of all Hero Classes in Afk Arena
    """
    Mage = "Mage"
    Tank = "Tank"
    Ranger = "Ranger"
    Support = "Support"
    Warrior = "Warrior"
