from typing import TYPE_CHECKING

from discord.ext import commands

from albedo_bot.database.schema.hero import Hero
from albedo_bot.cogs.hero.utils.base_hero import BaseHeroCog
from albedo_bot.utils.checks import check_config_permission
from albedo_bot.utils.message import EmbedWrapper, send_embed

if TYPE_CHECKING:
    from albedo_bot.bot import AlbedoBot


class HeroCog(BaseHeroCog):
    """
    A group of commands used to manager a players AFK Arena roster
    """

    @commands.group(name="hero")
    async def hero(self, ctx: commands.Context):
        """
        A group of commands used to display information about AFK arena
            characters, to view your AFK arena characters view the `roster`
            command

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        """

    @hero.command(name="register", aliases=["add"])
    @check_config_permission("guild_manager")
    async def register(self, ctx: commands.Context, hero_name: str):
        """
        Add/Register a new AFK Arena hero with the bot

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            name (str): name of hero getting added
        """
        await self._add_hero(ctx, hero_name)

    @hero.command(name="remove", aliases=["delete"])
    @check_config_permission("guild_manager")
    async def remove(self, ctx: commands.Context, hero_name: Hero):
        """
        Remove/delete an existing AFK Arena hero from the bot

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            name (str): [description]
        """
        await self._remove_hero(ctx, hero_name)

    @hero.command(name="show")
    async def show(self, ctx: commands.Context, hero_name: str = None):
        """
        Shows all the heroes currently added to the database

        Args:
            ctx (commands.Context): _description_
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


def setup(bot: "AlbedoBot"):
    """_summary_

    Args:
        bot (AlbedoBot): _description_
    """
    bot.add_cog(HeroCog(bot, require_registration=False))
