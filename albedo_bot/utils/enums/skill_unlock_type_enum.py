from albedo_bot.cogs.utils.mixins.enum_mixin import StrEnum


class HeroSkillUnlockTypeEnum(StrEnum):
    """
    An enumeration of all types of Heroes in AFK Arena
    """
    level = "level"
    ascension = "ascension"
    engraving = "engraving"
