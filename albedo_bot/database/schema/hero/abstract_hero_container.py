from albedo_bot.database.schema.hero.hero import Hero


class AbstractHeroContainer:
    """
    An abstract class that represents a class that has encapsulated a 
    Hero Schema
    """

    hero: Hero
