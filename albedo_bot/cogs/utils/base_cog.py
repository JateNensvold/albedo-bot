from typing import TYPE_CHECKING
from albedo_bot.utils.errors import CogCommandError, UnregisteredUserError
from albedo_bot.utils.message import EmbedWrapper, send_embed_exception

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

        if not ctx.invoked_subcommand and len(ctx.invoked_parents) == 0:
            await self.send_help(ctx)

    async def send_help(self, ctx: commands.Context):
        """_summary_

        Args:
            ctx (commands.context): _description_
        """
        embed_wrapper = EmbedWrapper(
            title="Invalid command",
            description=(
                f"`{ctx.message.content}` is an invalid command. Use "
                f"`{self.bot.default_prefix}help {ctx.command}` to learn more about the valid "
                "commands available"))
        await send_embed_exception(
            ctx, CogCommandError(embed_wrapper=embed_wrapper))

    def __init__(self, bot: "AlbedoBot", require_registration: bool = True):
        """_summary_

        Args:
            bot (AlbedoBot): _description_
            require_registration (bool, optional): _description_. Defaults to True.
        """
        self.bot = bot
        self.require_registration = require_registration

    async def is_registered(self, user: User):
        """
        Check if a player is already registered with the bot

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
