from typing import List, Union
from discord.ext import commands
from discord import Member

from albedo_bot.cogs.utils.base_cog import BaseCog
from albedo_bot.database.schema.hero import (
    Hero, HeroInstance, HeroInstanceTuple, HeroList)
from albedo_bot.utils.message import send_message


from albedo_bot.cogs.hero.utils.ascension import valid_ascension
from albedo_bot.cogs.hero.utils.engraving import (
    valid_engraving, engraving_range)
from albedo_bot.cogs.hero.utils.furniture import (
    valid_furniture, furniture_range)
from albedo_bot.cogs.hero.utils.signature_item import (
    valid_signature_item, signature_item_range)


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

        if not self.check_input(ctx, hero, ascension, signature_item,
                                furniture, engraving):
            return

        hero_instance_select = self.select(HeroInstance).where(
            HeroInstance.hero_id == hero.id, HeroInstance.player_id == player.id)
        hero_instance_result = await self.execute(hero_instance_select).first()

        if hero_instance_result is None:
            hero_instance_result = HeroInstance(
                hero.id, player.id, None, None, None, None)
            hero_instance_result.player_id = player.id
            hero_instance_result.hero_id = hero.id
        hero_instance_result.ascension_level = ascension
        hero_instance_result.signature_level = signature_item
        hero_instance_result.furniture_level = furniture
        hero_instance_result.engraving_level = engraving

        self.bot.session.add(hero_instance_result)

        hero_message = self.fetch_heroes([hero_instance_result])
        await send_message(ctx, hero_message, css=True)

    def check_input(self, ctx: commands.Context, hero: Hero, ascension: Union[str, int],
                    signature_item: int, furniture: int, engraving: int):
        """_summary_

        Args:
            ctx (Context): _description_
            hero (Hero): _description_
            ascension (Union[str, int]): _description_
            signature_item (int): _description_
            furniture (int): _description_
            engraving (int): _description_

        Returns:
            _type_: _description_
        """
        if not valid_ascension(ascension):
            ctx.send(
                f"The provided ascension value({ascension}) is not valid, "
                f"valid ascension values are ({signature_item_range(hero)}")
            return False
        if not valid_signature_item(hero, signature_item):
            ctx.send(
                f"The provided SI value({furniture}) is not valid for {hero.name}"
                f"({signature_item_range(hero)}")
            return False
        if not valid_furniture(hero, furniture):
            ctx.send(
                f"The provided furniture value({furniture}) is not valid for "
                f"{hero.name}({furniture_range(hero)}")
            return False
        if not valid_engraving(hero, engraving):
            ctx.send(
                f"The provided engraving value({furniture}) is not valid for "
                f"{hero.name}({engraving_range(hero)}")
            return False
        return True

    async def fetch_roster(self, discord_id: int):
        """_summary_

        Args:
            discord_id (int): _description_
        """

        hero_instance_select = self.select(HeroInstance).where(
            HeroInstance.player_id == discord_id)

        roster_results = await self.execute(hero_instance_select).all()

        return await self.fetch_heroes(roster_results)

    async def fetch_heroes(self, hero_list: List[HeroInstanceTuple]):
        """_summary_

        Args:
            hero_list (List[HeroInstance]): _description_
        """
        # hero_result_list = []
        # for hero_instance in hero_list:
        #     print(hero_instance, type(hero_instance))
        #     hero_select = self.select(Hero).where(
        #         Hero.id == hero_instance.hero_id)
        #     hero_result = await self.execute(hero_select).first()
        #     hero_tuple = HeroInstanceTuple(hero_result.name, hero_instance.hero_id,
        #                                    hero_instance.signature_level,
        #                                    hero_instance.furniture_level,
        #                                    hero_instance.ascension_level.name,
        #                                    hero_instance.engraving_level)
        #     hero_result_list.append(hero_tuple)
        heroes_message_object = HeroList(self.bot, hero_list)
        output = await heroes_message_object.async_str()
        return output
