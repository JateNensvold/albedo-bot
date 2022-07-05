from typing import TYPE_CHECKING
from albedo_bot.utils.errors import UnregisteredUserError

from discord.ext import commands
from discord import User

from albedo_bot.cogs.utils.mixins.database_mixin import DatabaseMixin
from albedo_bot.database.schema.player import Player

if TYPE_CHECKING:
    from albedo_bot.bot import AlbedoBot


class BaseCog(commands.Cog, DatabaseMixin):
    """_summary_

    Args:
        commands (_type_): _description_
        DatabaseMixin (_type_): _description_
    """

    async def cog_after_invoke(self, ctx: commands.Context):
        """_summary_

        Args:
            ctx (commands.Context): _description_
        """
        # if not ctx.invoked_subcommand:
        #     await self.send_help(ctx)

    async def send_help(self, ctx: commands.Context):
        """_summary_

        Args:
            ctx (commands.context): _description_
        """
        await ctx.send_help(ctx.command)

    def __init__(self, bot: "AlbedoBot", require_registration: bool = True):
        """_summary_

        Args:
            bot (AlbedoBot): _description_
            require_registration (bool, optional): _description_. Defaults to True.
        """
        self.bot = bot
        self.require_registration = require_registration

    async def is_registered(self, user: User):
        """_summary_

        Args:
            author (User): _description_
        """
        player_select = self.db_select(Player).where(
            Player.discord_id == user.id)
        player_result = await self.db_execute(player_select).first()

        if player_result is None:
            raise UnregisteredUserError(
                f"Register your discord account with "
                f"{self.bot.user.mention} to gain access to this command")
        return True

    # pylint: disable=invalid-overridden-method
    async def cog_check(self, ctx: commands.Context):
        """_summary_

        Args:
            ctx (commands.Context): _description_
        """
        if not self.require_registration:
            return True
        output = await self.is_registered(ctx.author)
        return output
