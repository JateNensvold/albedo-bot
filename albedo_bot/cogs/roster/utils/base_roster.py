
from datetime import datetime
import pprint
import io

from typing import TYPE_CHECKING, List
from image_processing.processing.async_processing.processing_status import ProcessingStatus
import jsonpickle
from discord.ext import commands
from discord import Member, User, Message, File

from image_processing.afk.hero.hero_data import RosterJson
from image_processing.processing.processing_client import ProcessingClient

import albedo_bot.config as config
from albedo_bot.database.schema.guild import Guild
from albedo_bot.database.schema.player.player import Player
from albedo_bot.cogs.utils.base_cog import BaseCog
from albedo_bot.utils.errors import CogCommandError, RemoteProcessingError
from albedo_bot.utils.message.message_send import (
    EmbedWrapper, edit_message, send_embed)
from albedo_bot.cogs.hero.utils import (
    AscensionValue, SignatureItemValue, EngravingValue, FurnitureValue)
from albedo_bot.database.schema.hero import (
    Hero, HeroInstance)
from albedo_bot.database.schema.hero.hero_instance import (
    HeroInstanceData, HeroList, HeroUpdateStatus)
from albedo_bot.utils.enums.ascension_enum import AscensionValues
from albedo_bot.utils import emoji

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

        self.failed_roster_str = (
            f"Please contact an admin or {bot.owner_string} "
            f"and give them the image that failed, or upload the "
            "failed image into any debugging channels available")

    # pylint: disable=no-member
    @BaseCog.admin.group(name="roster")
    async def roster_admin(self, ctx: commands.Context):
        """
        A group of roster commands that require elevated permissions to run

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        """

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
            HeroInstance.hero_id == hero.id,
            HeroInstance.player_id == player.id)
        hero_instance_result = await self.db_execute(
            hero_instance_select).first()

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
        """
        Fetch the hero strings for the heroes found in hero_list

        Args:
            hero_list (List[HeroInstance]): list of heroes to fetch strings for
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
        unknown_hero_list: list[HeroInstanceData] = []

        temporary_holdover_message: Message = None
        for image_number, attachment in enumerate(ctx.message.attachments):
            embed_wrapper = EmbedWrapper(
                title="Processing Roster... ",
                description=(f"Currently processing image {image_number}"))
            if temporary_holdover_message is None:
                temporary_holdover_messages = await send_embed(
                    ctx, embed_wrapper=embed_wrapper)
                temporary_holdover_message = temporary_holdover_messages[0]
            else:
                await edit_message(ctx,
                                   message=temporary_holdover_message,
                                   embed_wrapper=embed_wrapper)
            command_list = [str(attachment)]
            if config.VERBOSE:
                command_list.append("-v")
            try:
                processing_response = ProcessingClient().remote_compute_results(
                    config.PROCESSING_SERVER_ADDRESS,
                    config.PROCESSING_SERVER_TIMEOUT_MILLISECONDS,
                    command_list)
                if processing_response.status == ProcessingStatus.success:
                    roster_json = processing_response.result
                elif processing_response.status == ProcessingStatus.failure:
                    error_message = processing_response.message
                    raise RemoteProcessingError(error_message)
                else:
                    raise RemoteProcessingError(
                        embed_wrapper=EmbedWrapper(
                            tittle="Unknown Processing Response",
                            description=(
                                f"Received unknown processing response of: "
                                f"`{processing_response.status} with a message "
                                f"of\n{processing_response.message}")))
            except Exception as exception:
                embed_wrapper = EmbedWrapper(
                    title="Roster Detection Failed",
                    description=(
                        f"Roster detection has failed due to `{exception}`.\n\n"
                        f"{self.failed_roster_str}"))
                raise CogCommandError(
                    embed_wrapper=embed_wrapper) from exception

            if config.VERBOSE:
                pprint.pprint(roster_json.json_dict())

            for detected_index, detected_hero_data in enumerate(
                    roster_json.hero_data_list):

                if detected_hero_data.name.valid_match():
                    detected_hero_name = detected_hero_data.name.hero_name
                else:
                    detected_hero_name = str(detected_hero_data.name)

                if detected_hero_name in self.hero_alias:
                    hero_database_name = self.hero_alias.get(
                        detected_hero_name)
                    hero_select = self.db_select(Hero).where(
                        Hero.name == hero_database_name)
                    hero_result = await self.db_execute(hero_select).first()
                else:
                    hero_select = self.db_select(Hero).where(
                        Hero.name.ilike(f"{detected_hero_name}%"))
                    hero_result = await self.db_execute(hero_select).first()

                if not hero_result:
                    unknown_hero_tuple = HeroInstanceData(
                        hero_name=(
                            f"Image {image_number}, Position {detected_index} "
                            f"- {detected_hero_name}"),
                        hero_id=None,
                        signature_level=detected_hero_data.signature_item.label,
                        furniture_level=detected_hero_data.furniture.label,
                        ascension_level=AscensionValues[
                            detected_hero_data.ascension.label],
                        engraving_level=detected_hero_data.engraving.label)
                    unknown_hero_list.append(unknown_hero_tuple)
                    continue

                hero_tuple = HeroInstanceData(
                    hero_name=hero_result.name,
                    hero_id=hero_result.id,
                    signature_level=detected_hero_data.signature_item.label,
                    furniture_level=detected_hero_data.furniture.label,
                    ascension_level=AscensionValues[
                        detected_hero_data.ascension.label],
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
            final_hero_instance: HeroInstance = hero_instance_result
            if hero_instance_result is None:
                hero_tuple.hero_update_status = HeroUpdateStatus.NEW_HERO
                updated_hero_list.append(hero_tuple)
                final_hero_instance = new_hero_instance
            # Updated hero
            elif new_hero_instance > hero_instance_result:
                hero_tuple.hero_update_status = HeroUpdateStatus.UPDATED_HERO
                updated_hero_list.append(hero_tuple)
                final_hero_instance.update_from_instance(new_hero_instance)
            else:
                continue
            await self.db_add(final_hero_instance)

        if len(updated_hero_list) == 0:
            heroes_result_str = "No Hero updates detected"
        else:
            heroes_result_str = await self.fetch_heroes(updated_hero_list)

        description = heroes_result_str
        send_embed_kwargs = {}
        if len(unknown_hero_list) > 0:
            unknown_heroes_result_str = await self.fetch_heroes(
                unknown_hero_list)
            description = (
                f"{description}\n\n"
                "```The following unknown heroes were found in your roster\n"
                f"{self.failed_roster_str}```\n"
                f"{unknown_heroes_result_str}")
            send_embed_kwargs["embed_color"] = "yellow"
            send_embed_kwargs["emoji"] = emoji.warning

        # Delete the holdover message
        await temporary_holdover_message.delete()

        await send_embed(ctx,
                         embed_wrapper=EmbedWrapper(description=description),
                         **send_embed_kwargs)

    async def clear_roster(self, ctx: commands.Context, discord_user: User):
        """_summary_

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            discord_user (User): _description_
        """

        hero_instances_select = self.db_select(HeroInstance).where(
            HeroInstance.player_id == discord_user.id)

        hero_instance_objects = await self.db_execute(
            hero_instances_select).all()

        for hero_instance_object in hero_instance_objects:
            await self.db_delete(hero_instance_object)

        await send_embed(ctx, embed_wrapper=EmbedWrapper(
            description=(f"Roster cleared for {discord_user.mention}")))

    async def dump_rosters(self, ctx: commands.Context):
        """_summary_

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        """

        hero_instance_select = self.db_select(
            HeroInstance, Player, Hero, Guild
        ).join(
            HeroInstance, Player.discord_id == HeroInstance.player_id
        ).join(
            Hero, Hero.id == HeroInstance.hero_id
        ).join(
            Guild, Guild.discord_id == Player.guild_id
        ).order_by(
            Player.discord_id)
        player_roster_rows = await self.db_execute(
            hero_instance_select).all_objects()
        temporary_message_description = "Fetching information from database..."

        temporary_messages = await send_embed(
            ctx, embed_wrapper=EmbedWrapper(
                title="Dumping player rosters...",
                description=temporary_message_description))

        temporary_message_description = (
            f"{temporary_message_description} selected "
            f"{len(player_roster_rows)} rows\n Generating CSV...")

        await edit_message(ctx, message=temporary_messages[0],
                           embed_wrapper=EmbedWrapper(
                               title="Generating CSV...",
                               description=temporary_message_description))

        hero_instance_strings: list[str] = []
        player_set: set[int] = set()

        for hero_row in player_roster_rows:

            hero_instance: HeroInstance = hero_row[0]
            player: Player = hero_row[1]
            hero: Hero = hero_row[2]
            guild: Guild = hero_row[3]
            player_set.add(player.discord_id)

            hero_instance_str = (
                f"{player.name},{guild.name},{hero.name},"
                f"{hero_instance.ascension_level},"
                f"{hero_instance.signature_level},"
                f"{hero_instance.furniture_level},"
                f"{hero_instance.engraving_level}")
            hero_instance_strings.append(hero_instance_str)

        buffer = io.BytesIO(str.encode("\n".join(hero_instance_strings)))
        discord_file = File(
            buffer, filename=f"players_hero_dump_{str(datetime.now())}.csv")

        await temporary_messages[0].delete()
        await send_embed(ctx,
                         embed_wrapper=EmbedWrapper(description=(
                             f"Dumped {len(player_roster_rows)} lines, from "
                             f"{len(player_set)} players")),
                         file=discord_file)
