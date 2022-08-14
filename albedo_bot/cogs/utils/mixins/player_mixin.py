from typing import TYPE_CHECKING

from discord import Member
from albedo_bot.cogs.utils.mixins.database_mixin import DatabaseMixin
from albedo_bot.database.schema.player import Player, PlayerAvailability


if TYPE_CHECKING:
    from albedo_bot.bot import AlbedoBot


class PlayerMixin(DatabaseMixin):
    """
    A collection of utility functions around manipulating entries in the
        Player Database
    """

    bot: "AlbedoBot"

    async def get_player(self, author: Member):
        """
        Get a player from the database given a discord member

        Args:
            emoji_name (str): member to get player for
        """
        player_select = self.db_select(Player).where(
            Player.discord_id == author.id)
        return await self.db_execute(player_select).first()

    async def get_player_availability(self, author: Member):
        """
        Get a players availability entries from the database given a
        discord member

        Args:
            author (Member): member to get availability for
        """
        player_select = self.db_select(PlayerAvailability).where(
            PlayerAvailability.player_id == author.id)
        return await self.db_execute(player_select).all()
