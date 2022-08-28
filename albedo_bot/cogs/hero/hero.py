from typing import TYPE_CHECKING

from discord.ext import commands

from albedo_bot.cogs.hero.utils.converter.ascension_type import AscensionType
from albedo_bot.cogs.hero.utils.converter.hero_class import HeroClass
from albedo_bot.cogs.hero.utils.converter.hero_faction import HeroFaction
from albedo_bot.cogs.hero.utils.converter.hero_type import HeroType
from albedo_bot.database.schema.hero import Hero
from albedo_bot.cogs.hero.utils.base_hero import BaseHeroCog
from albedo_bot.utils.message import EmbedWrapper, send_embed
from albedo_bot.cogs.hero.utils.converter.hero import HeroValue

if TYPE_CHECKING:
    from albedo_bot.bot import AlbedoBot


class HeroCog(BaseHeroCog):
    """
    A group of commands used to manager a players AFK Arena roster
    """

    @BaseHeroCog.hero_admin.command(name="register", aliases=["add"])
    async def register(self, ctx: commands.Context, hero_name: str,
                       hero_faction: HeroFaction, hero_class: HeroClass,
                       hero_type: HeroType, ascension_tier: AscensionType):
        """
        Add/Register a new AFK Arena hero with the bot

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            name (str): name of hero getting added
        """

        await self._add_hero(ctx, hero_name, hero_faction, hero_class,
                             hero_type, ascension_tier)

    @BaseHeroCog.hero_admin.command(name="remove", aliases=["delete"])
    async def remove(self, ctx: commands.Context, hero_name: HeroValue):
        """
        Remove/delete an existing AFK Arena hero from the bot

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            name (str): [description]
        """
        await self._remove_hero(ctx, hero_name.hero)

    @BaseHeroCog.hero_admin.command(name="show")
    async def show(self, ctx: commands.Context, hero_name: str = None):
        """
        Shows all the heroes currently added to the database

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            hero_name (str, optional): Name or prefix of heroes to show. When
                no name is provided all heroes are returned.
        """
        if hero_name is None:
            hero_instances_select = self.db_select(Hero)
        else:
            hero_instances_select = self.db_select(
                Hero).where(Hero.name.ilike(f"{hero_name}%"))
        hero_instances_result = await self.db_execute(
            hero_instances_select).all()

        hero_list = "\n".join((f"`{hero_object}`"
                               for hero_object in hero_instances_result))

        await send_embed(ctx, embed_wrapper=EmbedWrapper(
            title="Hero List",
            description=hero_list))

    @BaseHeroCog.hero_admin.command(name="autoload", aliases=[])
    async def autoload(self, ctx: commands.Context):
        """
        Automatically check if any hero updates/additions have occurred in the
        following git repo
        https://github.com/Dae314/AFKBuilder/blob/main/src/stores/HeroData.js

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            name (str): name of hero getting added
        """

        await self._auto_load(ctx)

    @BaseHeroCog.hero_admin.group(name="image")
    async def hero_image(self, ctx: commands.Context):
        """
        Parent command for all hero image sub commands

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        """

    @hero_image.command(name="add", aliases=["upload"])
    async def add_images(self, ctx: commands.Context, hero: HeroValue,
                         insertion_index: int = -1):
        """
        Add a hero image to the hero Database, this will also update the image
        recognition used to detect heroes. I.e. you can add skin for a hero and
        it will start getting recognized.

        *Note: This command triggers a full rebuild of the keypoint database
        used for hero detection by the image recognition library, that
        can take several dozen seconds

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            hero (Hero): the hero to add an image fro
            insertion_index (int, optional): The index that the image should be
                assigned in the hero image database, the image with the lowest
                index will be the emoji that is shown when a hero is
                displayed to players. Defaults to -1 which will be used to
                append the hero to the image database instead of insert.
        """
        await self._add_image(ctx, hero.hero, insertion_index)

    @hero_image.command(name="remove", aliases=["delete"])
    async def remove_image(self, ctx: commands.Context, hero: HeroValue,
                           image_index: int):
        """
        Remove an optional HeroPortrait image from the database, any
        image that is marked as required cannot be removed

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            hero (Hero): the hero to add an image for
            image_index (int): the image index of the image to remove
        """
        self._remove_image(ctx, hero.hero, image_index)

    @hero_image.command(name="display", aliases=["show"])
    async def show_images(self, ctx: commands.Context, hero: HeroValue):
        """
        Display all the images/portraits for a hero.

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            hero (Hero): the hero to display the images of

        """
        await self._show_image(ctx, hero.hero)


async def setup(bot: "AlbedoBot"):
    """_summary_

    Args:
        bot (AlbedoBot): _description_
    """
    await bot.add_cog(HeroCog(bot))
