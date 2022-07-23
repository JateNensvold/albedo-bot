
from discord.ext import commands

from albedo_bot.cogs.utils.base_cog import BaseCog
from albedo_bot.database.schema.hero import Hero
from albedo_bot.database.schema.hero.hero import (
    HeroAscensionEnum, HeroClassEnum, HeroFactionEnum, HeroTypeEnum)
from albedo_bot.utils.errors import CogCommandError
from albedo_bot.utils.message import EmbedWrapper, send_embed


class BaseHeroCog(BaseCog):
    """_summary_
    """

    async def _find_hero(self, hero_name: Hero):
        """
        Search for a hero with the name 'hero_name' in the database. Return true if
        there is a match, return False otherwise

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            hero_name ([type]): name of hero to look for

        Returns:
            [type]: Return 'hero_object' if found in the heroes table,
                None otherwise
        """

        hero_select = self.db_select(Hero).where(
            Hero.name == hero_name)
        hero_object = await self.db_execute(hero_select).first()

        return hero_object

    async def _add_hero(self, ctx: commands.Context,
                        hero_name: str,
                        hero_faction: HeroFactionEnum,
                        hero_class: HeroClassEnum,
                        hero_type: HeroTypeEnum,
                        ascension_tier: HeroAscensionEnum):
        """
        Add a hero to the hero database

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            hero_name (str): name of hero to add
        """
        hero_object: Hero = await self._find_hero(hero_name)
        if hero_object is None:
            new_hero = Hero(name=hero_name, hero_faction=hero_faction,
                            hero_class=hero_class, hero_type=hero_type,
                            ascension_tier=ascension_tier)
            await self.db_add(new_hero)

            await send_embed(ctx, embed_wrapper=EmbedWrapper(
                description=(f"Added new hero `{hero_name}` as `{new_hero}`")))
        else:

            embed_wrapper = EmbedWrapper(
                title="Hero Already Registered",
                description=(
                    f"A hero with the name `{hero_name}` has already been "
                    f"registered as `{hero_object}`"))
            raise CogCommandError(embed_wrapper=embed_wrapper)

    async def _remove_hero(self, ctx: commands.Context, hero_object: Hero):
        """
        Remove a hero from the database

        Args:
            ctx (Context): _description_
            hero_object (Hero): Hero getting removed
        """
        await self.db_delete(hero_object)

        await send_embed(ctx, embed_wrapper=EmbedWrapper(
            description=(f"Removed hero `{hero_object}` from hero database")))
