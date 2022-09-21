import datetime
from typing import TYPE_CHECKING, Union

from discord.ext import commands
from discord import User

from albedo_bot.database.schema.player.player import Player
from albedo_bot.utils.checks import _is_registered, check_config_permission
from albedo_bot.utils.errors import CogCommandError
from albedo_bot.utils.message.message_send import EmbedWrapper, send_embed_exception
from albedo_bot.cogs.utils.mixins.database_mixin import DatabaseMixin

if TYPE_CHECKING:
    from albedo_bot.bot import AlbedoBot


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

    @commands.group(name="admin", allow_duplicate=True, cog=False)
    @check_config_permission("admin")
    async def admin(self, ctx: User):
        """
        A group of commands that require elevated permissions to run

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        """

        # *Ensure that any commands/groups that inherit from this one are not
        # imported/defined before their parent otherwise the admin command
        # cannot be used across multiple cogs
        # i.e 

        # //file1.py
        # Class GrandParentCog(ParentCog)

        # //file2.py
        # class ParentCog(BaseCog)

        # //file3.py
        # class BaseCog
                    
        # ParentCog cannot get imported before GrandParentCog without
        # breaking any inherited admin commands

        # TL;DR: Always import the topmost cog first

    # def _inject(self, bot):
    #     command_list: list[commands.Group,
    #                        commands.command] = self.get_commands()
    #     for index, command in enumerate(self.__cog_commands__):
    #         print(index, command)

        # return super()._inject(bot)

    async def cog_after_invoke(self, ctx: commands.Context):
        """
        Used to invoke send_help when a command Group is invoked without a
            subcommand

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        """

        command: Union[commands.Command, commands.Group] = ctx.command

        # Currently it is not possible to detect if a message has already
        #   been sent on a ctx object. It is assumed that if a command failed
        #   then the bot error handling has taken over. If a command did not
        #   fail then we will send the help message for a group being invoked
        # without a subcommand
        if (not ctx.invoked_subcommand and len(ctx.invoked_parents) == 0 and
                isinstance(command, commands.Group)):
            await self.send_help(ctx)

    async def send_help(self, ctx: commands.Context):
        """_summary_

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        """
        embed_wrapper = EmbedWrapper(
            title="Invalid command",
            description=(
                f"`{ctx.message.content}` is an invalid command. Use "
                f"`{self.bot.default_prefix}help {ctx.command}` to learn more about the valid "
                "commands available"))
        await send_embed_exception(
            ctx, CogCommandError(embed_wrapper=embed_wrapper))

    async def update_player(self, player: User):
        """
        Update the access_time in the `Player` object associated with `player`

        Args:
            player (User): player to update access_time of
        """
        select_statement = self.db_select(Player).where(
            Player.discord_id == player.id)

        player_object = await self.db_execute(select_statement).first()

        player_object.access_time = datetime.datetime.utcnow()
        await self.db_add(player_object)

    # pylint: disable=invalid-overridden-method

    async def cog_check(self, ctx: commands.Context):
        """_summary_

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        """
        if not self.require_registration:
            return True
        output = await _is_registered(ctx.bot, ctx.author)
        return output
