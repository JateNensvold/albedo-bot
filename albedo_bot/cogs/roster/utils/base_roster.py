from typing import List
from discord.ext import commands
from discord import Member

from albedo_bot.cogs.utils.base_cog import BaseCog
from albedo_bot.database.schema.hero import (
    Hero, HeroInstance, HeroInstanceTuple, HeroList)
from albedo_bot.utils.message import send_message

from albedo_bot.cogs.hero.utils import (
    check_ascension, check_signature_item, check_furniture, check_engraving)


class BaseRosterCog(BaseCog):
    """_summary_

    Args:
        commands (_type_): _description_
    """

    async def add_hero(self, ctx: commands.Context, player: Member, hero: Hero,
                       ascension: str, signature_item: int, furniture: int,
                       engraving: int):
        """[summary]

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            name (str): [description]
        """
        hero_ascension = check_ascension(ascension)
        check_signature_item(hero, signature_item)
        check_furniture(hero, furniture)
        check_engraving(hero, engraving)

        hero_instance_select = self.db_select(HeroInstance).where(
            HeroInstance.hero_id == hero.id, HeroInstance.player_id == player.id)
        hero_instance_result = await self.db_execute(hero_instance_select).first()

        if hero_instance_result is None:
            hero_instance_result = HeroInstance(
                hero.id, player.id, signature_item, furniture, hero_ascension, engraving)
        else:
            hero_instance_result.ascension_level = hero_ascension
            hero_instance_result.signature_level = signature_item
            hero_instance_result.furniture_level = furniture
            hero_instance_result.engraving_level = engraving

        self.db_add(hero_instance_result)

        hero_instance_tuples = await HeroInstanceTuple.from_hero_instance(
            self, hero_instance_result)

        await send_message(ctx,
                           await self.fetch_heroes(hero_instance_tuples))

    async def fetch_roster(self, discord_id: int):
        """_summary_

        Args:
            discord_id (int): _description_
        """

        hero_instance_select = self.db_select(HeroInstance).where(
            HeroInstance.player_id == discord_id)

        roster_results = await self.db_execute(hero_instance_select).all()

        hero_instance_tuples = await HeroInstanceTuple.from_hero_instance(
            self, roster_results)

        return await self.fetch_heroes(hero_instance_tuples)

    async def fetch_heroes(self, hero_list: List[HeroInstanceTuple]):
        """_summary_

        Args:
            hero_list (List[HeroInstance]): _description_
        """
        heroes_message_object = HeroList(self.bot, hero_list)
        output = await heroes_message_object.async_str()

        return output
