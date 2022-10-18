from typing import Union, TYPE_CHECKING

from discord.ext import commands

import albedo_bot.config as config
from albedo_bot.database.schema.hero.hero import Hero
from albedo_bot.cogs.utils.mixins.database_mixin import DatabaseMixin
from albedo_bot.cogs.hero.utils.converter.hero_value_mixin import (
    HeroValueMixin)
from albedo_bot.database.schema.hero.abstract_hero_container import (
    AbstractHeroContainer)

if TYPE_CHECKING:
    from albedo_bot.bot import AlbedoBot


class HeroValue(HeroValueMixin, DatabaseMixin, AbstractHeroContainer):
    """
    A wrapper class around Hero to do argument conversion into Hero objects
    """

    def __init__(self, hero: Hero = None):
        """_summary_

        Args:
            si_value (int, optional): _description_. Defaults to None.
            hero (Hero, optional): _description_. Defaults to None.
            auto_detect (bool, optional): _description_. Defaults to None.
        """

        self.hero = hero

    async def init(self, argument: Union[int, str], ctx: commands.Context,
                   hero: Hero = None):
        """
        Initialize the arguments needed to create a HeroValue

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        """
        self.bot: "AlbedoBot" = ctx.bot

        self.hero = await self.check(ctx, argument)

    async def check(self, ctx: commands.Context, argument: Union[str, int]):
        """
        Convert a hero Name or id into a database Hero object

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            argument (Union[str, int]): _description_

        Raises:
            BadArgument: Occurs when a string or integer that is not
                associated with a hero is provided

        Returns:
            Hero: returns the hero associated with the conversion argument that
                was provided
        """
        hero_alias = config.objects.hero_alias

        try:
            try:
                int_argument = int(argument)
                hero_instance_select = self.db_select(
                    Hero).where(Hero.id == int_argument)
                hero_instance_result = await self.db_execute(
                    hero_instance_select).first()
            except ValueError as exception:
                hero_instances_select = self.db_select(
                    Hero).where(Hero.name == argument)
                hero_instances_result = await self.db_execute(
                    hero_instances_select).all()
                if len(hero_instances_result) == 1:
                    return hero_instances_result[0]

                hero_instances_select = self.db_select(
                    Hero).where(Hero.name.ilike(f"{argument}%"))
                hero_instances_result = await self.db_execute(
                    hero_instances_select).all()

                if len(hero_instances_result) == 1:
                    hero_instance_result = hero_instances_result[0]
                elif len(hero_instances_result) == 0 and argument in hero_alias:
                    hero_database_name = hero_alias.get(argument)
                    hero_instance_select = self.db_select(Hero).where(
                        Hero.name == hero_database_name)
                    hero_instance_result = await self.db_execute(
                        hero_instance_select).first()
                elif len(hero_instances_result) == 0:
                    raise commands.BadArgument(
                        (f"Invalid hero name `{argument}` no hero matches "
                         "that name")) from exception
                else:
                    hero_names = [f"(\"{hero.name}\", {hero.id})"
                                  for hero in hero_instances_result]
                    hero_names_str = ", ".join(hero_names)
                    raise commands.BadArgument(
                        f"Invalid hero name `{argument}` too many Hero "
                        "matches. Choose one of the following heroes "
                        f"`[{hero_names_str}]`") from exception
            if hero_instance_result is None:
                raise AssertionError
            return hero_instance_result
        except AssertionError as exception:
            raise commands.BadArgument(
                f"Invalid hero name or id `{argument}`") from exception
