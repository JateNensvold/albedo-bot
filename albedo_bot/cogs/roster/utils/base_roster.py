
import pprint
from typing import TYPE_CHECKING, List

from discord.ext import commands
from discord import Member, User
from image_processing.processing_client import remote_compute_results

import albedo_bot.config as config
from albedo_bot.cogs.utils.base_cog import BaseCog
from albedo_bot.utils.errors import CogCommandError
from albedo_bot.utils.message import (
    EmbedWrapper, send_embed, send_embed_exception)
from albedo_bot.cogs.hero.utils import (
    AscensionValue, SignatureItemValue, EngravingValue, FurnitureValue)
from albedo_bot.database.schema.hero import (
    Hero, HeroInstance, HeroInstanceData, HeroList, AscensionValues)
from albedo_bot.database.schema.hero.hero_instance import (
    HeroUpdateStatus)
if TYPE_CHECKING:
    from albedo_bot.bot import AlbedoBot


class BaseRosterCog(BaseCog):
    """_summary_

    Args:
        commands (_type_): _description_
    """

    def __init__(self, bot: "AlbedoBot"):
        self.hero_alias = config.hero_alias
        super().__init__(bot)

    async def add_hero(self, ctx: commands.Context, player: Member, hero: Hero,
                       ascension: AscensionValue,
                       signature_item: SignatureItemValue,
                       furniture: FurnitureValue,
                       engraving: EngravingValue):
        """[summary]

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            name (str): [description]
        """

        hero_instance_select = self.db_select(HeroInstance).where(
            HeroInstance.hero_id == hero.id, HeroInstance.player_id == player.id)
        hero_instance_result = await self.db_execute(hero_instance_select).first()

        if hero_instance_result is None:
            hero_instance_result = HeroInstance(
                hero.id,
                player.id,
                signature_item.si_value,
                furniture.furniture_value,
                ascension.ascension_value,
                engraving.engraving_value)
        else:
            hero_instance_result.ascension_level = ascension.ascension_value
            hero_instance_result.signature_level = signature_item.si_value
            hero_instance_result.furniture_level = furniture.furniture_value
            hero_instance_result.engraving_level = engraving.engraving_value

        await self.db_add(hero_instance_result)

        hero_instance_tuples = await HeroInstanceData.from_hero_instance(
            self, hero_instance_result)
        added_heroes = await self.fetch_heroes(hero_instance_tuples)
        await send_embed(ctx, embed_wrapper=EmbedWrapper(
            description=("The following heroes have been added successfully\n "
                         f"{added_heroes}")))

    async def remove_hero(self, ctx: commands.Context, player: User,
                          hero: Hero,):
        """[summary]

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            name (str): [description]
        """

        hero_instance_select = self.db_select(HeroInstance).where(
            HeroInstance.hero_id == hero.id,
            HeroInstance.player_id == player.id)
        hero_instance_result = await self.db_execute(
            hero_instance_select).first()

        if hero_instance_result is None:
            embed_wrapper = EmbedWrapper(
                title="Missing hero",
                description=("You do not have the following hero "
                             f"`{hero.name}` in your roster"))
            raise CogCommandError(embed_wrapper=embed_wrapper)
        else:
            hero_instance_tuples = await HeroInstanceData.from_hero_instance(
                self, hero_instance_result)
            removed_heroes = await self.fetch_heroes(hero_instance_tuples)

            await self.db_delete(hero_instance_result)
            await send_embed(ctx, embed_wrapper=EmbedWrapper(
                title="Removed Hero",
                description=(f"The following heroes have been successfully "
                             f"removed from your roster\n {removed_heroes}")))

    async def fetch_roster(self, discord_id: int):
        """_summary_

        Args:
            discord_id (int): _description_
        """

        hero_instance_select = self.db_select(HeroInstance).where(
            HeroInstance.player_id == discord_id)

        roster_results = await self.db_execute(hero_instance_select).all()

        hero_instance_tuples = await HeroInstanceData.from_hero_instance(
            self, roster_results)

        return await self.fetch_heroes(hero_instance_tuples)

    async def fetch_heroes(self, hero_list: List[HeroInstanceData]):
        """_summary_

        Args:
            hero_list (List[HeroInstance]): _description_
        """
        heroes_message_object = HeroList(self.bot, hero_list)
        output = await heroes_message_object.async_str()

        return output

    async def _upload(self, ctx: commands.Context):
        """
        Automatically detects the investment levels for all heroes in
        roster screenshots attached to this command

        Args:
            ctx (commands.Context): ctx (Context): invocation context
                containing information on how a discord event/command was
                invoked
        """

        author_id: int = ctx.author.id

        detected_hero_dict: dict[str, int] = {}
        detected_hero_list: list[HeroInstanceData] = []

        for image_number, attachment in enumerate(ctx.message.attachments):

            command_list = [str(attachment)]
            if config.VERBOSE:
                command_list.append("-v")
            roster_json = remote_compute_results(
                config.PROCESSING_SERVER_ADDRESS, 15000, command_list)
            if config.VERBOSE:
                pprint.pprint(roster_json.json_dict())

            for detected_index, detected_hero_data in enumerate(
                    roster_json.hero_data_list):

                if detected_hero_data.name in self.hero_alias:
                    hero_database_name = self.hero_alias.get(
                        detected_hero_data.name)
                    hero_select = self.db_select(Hero).where(
                        Hero.name == hero_database_name)
                    hero_result = await self.db_execute(hero_select).first()
                else:
                    hero_select = self.db_select(Hero).where(
                        Hero.name.ilike(f"{detected_hero_data.name}%"))
                    hero_result = await self.db_execute(hero_select).first()

                if not hero_result:
                    await send_embed_exception(
                        ctx, CogCommandError(embed_wrapper=EmbedWrapper(
                            title="Unknown Hero Detected",
                            description=(
                                "Unable to find detected hero with "
                                f"name: '{detected_hero_data.name}' in image "
                                f"{image_number}, position {detected_index}"))))
                    continue

                hero_tuple = HeroInstanceData(
                    hero_name=hero_result.name,
                    hero_id=hero_result.id,
                    signature_level=detected_hero_data.signature_item.label,
                    furniture_level=detected_hero_data.furniture.label,
                    ascension_level=AscensionValues[detected_hero_data.ascension.label],
                    engraving_level=detected_hero_data.engraving.label)

                hero_name = hero_tuple.hero_name
                if hero_name in detected_hero_dict:
                    hero_index = detected_hero_dict[hero_name]
                    detected_hero_list[hero_index] = max(
                        hero_tuple, detected_hero_list[hero_index])
                else:
                    detected_hero_dict[hero_name] = len(detected_hero_list)
                    detected_hero_list.append(hero_tuple)

        updated_hero_list: list[HeroInstanceData] = []

        for hero_tuple in detected_hero_list:
            hero_instance_select = self.db_select(HeroInstance).where(
                HeroInstance.player_id == author_id,
                HeroInstance.hero_id == hero_tuple.hero_id)

            hero_instance_result = await self.db_execute(
                hero_instance_select).first()
            new_hero_instance = HeroInstance.from_instance_tuple(
                hero_tuple, author_id)
            # New Hero
            if hero_instance_result is None:
                hero_tuple.hero_update_status = HeroUpdateStatus.NEW_HERO
                updated_hero_list.append(hero_tuple)
            # Updated hero
            elif new_hero_instance > hero_instance_result:
                hero_tuple.hero_update_status = HeroUpdateStatus.UPDATED_HERO
                updated_hero_list.append(hero_tuple)
            else:
                continue
            self.bot.session.add(new_hero_instance)

        if len(updated_hero_list) == 0:
            heroes_result_str = "No Hero updates detected"
        else:
            heroes_result_str = await self.fetch_heroes(updated_hero_list)
        await send_embed(ctx, embed_wrapper=EmbedWrapper(
            description=heroes_result_str))
