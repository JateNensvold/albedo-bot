from typing import TYPE_CHECKING, Union
from albedo_bot.utils.errors import CogCommandError, UnregisteredUserError
from albedo_bot.utils.message import EmbedWrapper, send_embed_exception

from discord.ext import commands
from discord import User

from albedo_bot.cogs.utils.mixins.database_mixin import DatabaseMixin
from albedo_bot.database.schema.player import Player

if TYPE_CHECKING:
    from albedo_bot.bot import AlbedoBot


# def group(name: str = None, allow_duplicate: bool = False, **attrs):
#     """A decorator that transforms a function into a :class:`.Group`.

#     This is similar to the :func:`.command` decorator but the ``cls``
#     parameter is set to :class:`Group` by default.

#     .. versionchanged:: 1.1
#         The ``cls`` parameter can now be passed.
#     """

#     def deduplication_decorator(func):
#         command_object = commands.group(name, **attrs)
#         output = command_object(func)
#         output.allow_duplicate = allow_duplicate
#         print(output, repr(output))
#         print(output.allow_duplicate)

#         # for attr in dir(output):
#         #     print(attr)
#         return output

#     return deduplication_decorator


class BaseCog(commands.Cog, DatabaseMixin):
    """_summary_

    Args:
        commands (_type_): _description_
        DatabaseMixin (_type_): _description_
    """
    command_dict = {}

    def __init__(self, bot: "AlbedoBot", require_registration: bool = True):
        """_summary_

        Args:
            bot (AlbedoBot): _description_
            require_registration (bool, optional): _description_. Defaults to True.
        """
        self.bot = bot
        self.require_registration = require_registration

    @commands.group(name="admin", allow_duplicate=True)
    async def admin(self, ctx: commands.Context):
        """
        A group of commands that require elevated permissions to run

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        """

    # def _inject(self, bot):
    #     command_list: list[commands.Group,
    #                        commands.command] = self.get_commands()
    #     for index, command in enumerate(self.__cog_commands__):

    #         if self.track_command(command):
    #             self

    #     return super()._inject(bot)

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
