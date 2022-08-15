
import datetime
from typing import TYPE_CHECKING

import discord
from discord import Member

from albedo_bot.cogs.utils.mixins.player_mixin import PlayerMixin
from albedo_bot.utils.enums.availability_enum import (
    AVAILABILITY_ENUM, NORMAL_TIME_FORMAT)
from albedo_bot.utils.select import Select, SelectOption
from albedo_bot.database.schema.player import PlayerAvailability

if TYPE_CHECKING:
    from albedo_bot.bot import AlbedoBot


class AvailabilitySelect(Select, PlayerMixin):
    """_summary_

    Args:
        Select (_type_): _description_
    """

    def __init__(self,
                 bot: "AlbedoBot",
                 options: list[SelectOption],
                 *args,
                 **kwargs):
        self.bot = bot

        super().__init__(options, *args, **kwargs)
        self.selection_translation: dict[str, SelectOption] = {}

        for selection_option in self.options:
            self.selection_translation[
                selection_option.label] = selection_option.original_value
        self.options = options

    async def callback(self, interaction: discord.Interaction):
        """
        Callback to change players availability settings

        Args:
            interaction (discord.Interaction): Interaction information from
                discord
        """
        author = interaction.user

        availability_objects = await self.get_player_availability(author)

        old_availability: dict[str, PlayerAvailability] = {}

        for availability_object in availability_objects:
            old_availability[
                availability_object.availability.name] = availability_object

        stale_availability: dict[str, PlayerAvailability] = {
            **old_availability}

        for selected_value in self.values:
            original_value = self.selection_translation[selected_value]
            # Leave these availability entries in the database because they
            #   are still selected
            if original_value.name in stale_availability:
                del stale_availability[original_value.name]
            else:
                player_availability = PlayerAvailability()
                player_availability.player_id = author.id
                player_availability.availability = original_value
                await self.db_add(player_availability)

        for availability_object in stale_availability.values():
            await self.db_delete(availability_object)

        # Delete availability entries that are no longer selected by the player
        if len(old_availability) == 0:
            message = ("Your current availability is set as "
                       f"`{', '.join(self.values)}`")
        else:
            old_availability_times: list[str] = []
            for availability_datetime in old_availability.values():
                old_availability_times.append(
                    availability_datetime.availability.value.strftime(
                        NORMAL_TIME_FORMAT))
            old_availability_str = ", ".join(old_availability_times)

            message = ("Your availability has been successfully updated from"
                       f"`[{old_availability_str}]` to "
                       f"`[{', '.join(self.values)}]`")
        await interaction.response.send_message(
            content=message, ephemeral=True)

    @ classmethod
    async def build_selection(cls, bot: "AlbedoBot", author: Member):
        """
        Build a AvailabilitySelect object for a discord member

        Args:
            bot (AlbedoBot): bot used to interact with database
            author (Member): author to build selection for

        Returns:
            AvailabilitySelect: selection for `author`
        """
        plater_util = PlayerMixin()
        plater_util.bot = bot

        availability_options: list[SelectOption] = []
        default_values: set[str] = set()

        availability_objects = await plater_util.get_player_availability(author)
        for availability_object in availability_objects:
            default_values.add(availability_object.availability.name)

        for availability_enum in AVAILABILITY_ENUM.list():
            availability_index = availability_enum.name
            availability_datetime = availability_enum.value
            normal_time = availability_datetime.strftime(NORMAL_TIME_FORMAT)

            next_normal_datetime: datetime.datetime = AVAILABILITY_ENUM[
                str((int(availability_index) + 1) % 24)].value

            next_normal_timestamp = next_normal_datetime.strftime(
                NORMAL_TIME_FORMAT)

            default = False
            if availability_index in default_values:
                default = True
            availability_options.append(
                SelectOption(original_value=availability_enum,
                             label=f"{normal_time}",
                             description=(
                                 f"{normal_time} - "
                                 f"{next_normal_timestamp}"),
                             default=default))

        availability_selection = AvailabilitySelect(
            bot=bot,
            options=availability_options,
            placeholder_text="Availability Preference",
            max_values=len(availability_options))
        return availability_selection
