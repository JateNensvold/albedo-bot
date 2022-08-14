
import datetime
from typing import Any, Awaitable, Callable, TYPE_CHECKING, Union

import discord
from discord import Member
from cachetools import cached

from albedo_bot.cogs.utils.mixins.database_mixin import DatabaseMixin
from albedo_bot.utils.enums.availability_enum import (
    AVAILABILITY_ENUM, NORMAL_TIME_FORMAT)
from albedo_bot.database.schema.player.player import Player
from albedo_bot.utils.enums.timezone_enum import TIMEZONE_ENUM

if TYPE_CHECKING:
    from albedo_bot.bot import AlbedoBot



FuncType = Callable[[Any], Awaitable[Any]]


class Select(discord.ui.Select):
    """_summary_

    Args:
        discord (_type_): _description_
    """

    def __init__(self,
                 options: list[discord.SelectOption],
                 callback: FuncType = None,
                 placeholder_text: str = "Select an option",
                 max_values: int = 1,
                 min_values: int = 1):
        super().__init__(placeholder=placeholder_text,
                         max_values=max_values, min_values=min_values, options=options)
        self._callback = callback

    async def callback(self, interaction: discord.Interaction):
        return await self._callback(self, interaction)


class SelectView(discord.ui.View):
    """_summary_

    Args:
        discord (_type_): _description_
    """

    def __init__(self, select_items: list[Select], timeout=180):
        """_summary_

        Args:
            select_items (list[Select]): _description_
            timeout (int, optional): _description_. Defaults to 180.
        """
        super().__init__(timeout=timeout)
        for selector in select_items:
            self.add_item(selector)


class AvailabilitySelect(Select, DatabaseMixin):
    """_summary_

    Args:
        Select (_type_): _description_
    """

    def __init__(self, bot: "AlbedoBot",  *args, **kwargs):
        self.bot = bot
        super().__init__(*args, **kwargs)

    async def callback(self, interaction: discord.Interaction):
        """_summary_

        Args:
            interaction (discord.Interaction): _description_
        """

        await interaction.response.send_message(
            content=("Your current availability is set as "
                     f"`{self.values}`"), ephemeral=True)


class TimezoneSelect(Select, DatabaseMixin):
    """_summary_

    Args:
        Select (_type_): _description_
    """

    def __init__(self, bot: "AlbedoBot",  *args, **kwargs):
        self.bot = bot
        super().__init__(*args, **kwargs)

    async def callback(self, interaction: discord.Interaction):
        """_summary_

        Args:
            interaction (discord.Interaction): _description_
        """

        author = interaction.user
        player_object = await self.get_player(author)
        print(self.values)
        current_timezone = self.values[0]
        timezone_enum = TIMEZONE_ENUM[current_timezone]

        print(timezone_enum.value)

        await interaction.response.send_message(
            content=("Your current timezone is set as "
                     f"`{self.values}`"), ephemeral=True)

    async def get_player(self, author: Member):
        """
        Fetches the player associated with a Member object

        Args:
            author (Member): player to fetch database entry for
        """

        player_select = self.db_select(Player).where(
            Player.discord_id == author.id)

        player_object = await self.db_execute(player_select).first()
        return player_object

    async def get_current_timezones(self,
                                    author: Member) -> Union[
                                        TIMEZONE_ENUM, None]:
        """
        Get the current timezone for a Member object

        Args:
            author (Member): author to get the timezone for

        Returns the current timezone entry for the player
        """
        player_object = await self.get_player(author)

        current_timezone = player_object.timezone
        return current_timezone


def build_availability_selection(bot: "AlbedoBot", author: Member):
    """_summary_
    """

    availability_options: list[discord.SelectOption] = []

    for availability_index, availability_datetime in AVAILABILITY_ENUM.tuple_list():
        normal_time = availability_datetime.strftime(NORMAL_TIME_FORMAT)
        # milliary_time = availability_datetime.strftime(
        #     MILITARY_TIME_FORMAT)
        next_normal_datetime: datetime.datetime = AVAILABILITY_ENUM[
            str((int(availability_index) + 1) % 24)].value

        next_normal_timestamp = next_normal_datetime.strftime(
            NORMAL_TIME_FORMAT)
        availability_options.append(
            discord.SelectOption(
                label=f"{normal_time}",
                description=(
                    f"{normal_time} - "
                    f"{next_normal_timestamp}")))

    availability_selection = AvailabilitySelect(
        bot=bot,
        options=availability_options,
        placeholder_text="Availability Preference",
        max_values=len(availability_options))
    return availability_selection


def build_timezone_selection(bot: "AlbedoBot", author: Member):
    """_summary_
    """

    timezone_selection_options: list[discord.SelectOption] = []

    for timezone_name, timezone_description in TIMEZONE_ENUM.tuple_list():
        timezone_selection_options.append(discord.SelectOption(
            label=timezone_name, description=timezone_description))

    timezone_selection = TimezoneSelect(bot,
                                        options=timezone_selection_options,
                                        placeholder_text="Timezone Preference")

    return timezone_selection

# Cache calls to this function and just return the same selectView


@cached(cache={})
def build_view(bot: "AlbedoBot", author: Member):
    """_summary_
    """
    timezone_selection = build_timezone_selection(bot, author)
    availability_selection = build_availability_selection(bot, author)

    return SelectView([timezone_selection, availability_selection])
