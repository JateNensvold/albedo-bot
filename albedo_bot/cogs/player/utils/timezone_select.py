
from typing import TYPE_CHECKING, Union

import discord
from discord import Member

from albedo_bot.utils.enums.timezone_enum import TIMEZONE_ENUM
from albedo_bot.utils.embeds.select import Select, SelectOption
from albedo_bot.cogs.utils.mixins.player_mixin import PlayerMixin

if TYPE_CHECKING:
    from albedo_bot.bot import AlbedoBot


class TimezoneSelect(Select, PlayerMixin):
    """_summary_

    Args:
        Select (_type_): _description_
    """

    def __init__(self, bot: "AlbedoBot",  *args, **kwargs):
        self.bot = bot
        super().__init__(*args, **kwargs)

    async def callback(self, interaction: discord.Interaction):
        """
        Callback to change players timezone settings

        Args:
            interaction (discord.Interaction): Interaction information from
                discord
        """

        author = interaction.user

        player_object = await self.get_player(author)
        previous_timezone = player_object.timezone

        timezone_enum = TIMEZONE_ENUM[self.values[0]]
        player_object.timezone = timezone_enum

        await self.db_add(player_object)

        previous_timezone_enum_str = (f"{previous_timezone}"
                                      f"({previous_timezone.value})")
        timezone_enum_str = f"{timezone_enum}({timezone_enum.value})"
        if previous_timezone is None:
            message = ("Your timezone has been set to "
                       f"`{timezone_enum_str}`")
        else:
            message = ("Your timezone has been successfully changed from "
                       f" `{previous_timezone_enum_str}` to "
                       f"`{timezone_enum_str}`")

        await interaction.response.send_message(
            content=message, ephemeral=True)

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

    @classmethod
    async def build_selection(cls, bot: "AlbedoBot", author: Member):
        """
        Build a TimezoneSelect for the provided member passed in


        Args:
            bot (AlbedoBot): bot with access to database
            author (Member): author to build selection for

        Returns:
            TimezoneSelect: selection for `author`
        """

        timezone_selection_options: list[SelectOption] = []
        plater_util = PlayerMixin()
        plater_util.bot = bot
        player_object = await plater_util.get_player(author)

        current_timezone = player_object.timezone

        for timezone_enum in TIMEZONE_ENUM.list():
            timezone_name = timezone_enum.name
            timezone_description = timezone_enum.value
            default = False
            if current_timezone and timezone_name == current_timezone.name:
                default = True
            timezone_selection_options.append(
                SelectOption(original_value=timezone_enum,
                             label=timezone_name, description=timezone_description,
                             default=default))

        timezone_selection = TimezoneSelect(
            bot, options=timezone_selection_options,
            placeholder_text="Timezone Preference")
        return timezone_selection
