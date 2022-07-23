
from typing import TYPE_CHECKING

from cachetools import cached
from cachetools.keys import hashkey
from discord.ext import commands
from discord import User

import albedo_bot.config as config
from albedo_bot.database.schema.player import Player
from albedo_bot.utils.errors import UnregisteredUserError

if TYPE_CHECKING:
    from albedo_bot.bot import AlbedoBot


@cached(config.PERMISSIONS_CACHE,
        key=lambda ctx, config_role_name: hashkey(ctx.author.id,
                                                  config_role_name.lower))
def _check_permission(ctx: commands.Context, config_role_name: str):
    """
    Lookup if the author of a message has equal or higher permissions than the
        permissions assigned to 'config_role_name'

    All players + command permissions are cached for 1 hour

    Args:
        ctx (commands.Context): invocation context containing information on how
            a discord event/command was invoked
        config_role_name (str): name of role in permissions config file
        ttl_hash (str)

    Returns:
        bool: True if the author has the required permissions level,
            False otherwise
    """
    required_permission = config.permissions.permission_name_lookup[
        config_role_name.lower()]

    return config.permissions.lookup(ctx.author) >= required_permission


def check_config_permission(config_role_name: str):
    """
    Decorate a bot command and check if the person making the call has
        permission to do so based on if their permissions level is higher than
        the `config_role_name` the command is decorated with

    Args:
        arg (_type_): _description_
    """

    def pred(ctx: commands.Context):
        """_summary_

        Args:
            ctx (_type_): _description_

        Returns:
            _type_: _description_
        """
        return _check_permission(ctx, config_role_name)
    return commands.check(pred)


async def _is_registered(bot: "AlbedoBot", user: User):
    """
    Check if a player is already registered with the bot

    Args:
        author (User): _description_
    """

    player_select = bot.db_select(Player).where(
        Player.discord_id == user.id)
    player_result = await bot.db_execute(player_select).first()

    if player_result is None:
        raise UnregisteredUserError(
            f"Register your discord account with "
            f"{bot.user.mention} to gain access to this command")
    return True


def is_registered():
    """_summary_
    """

    async def pred(ctx: commands.Context):
        """_summary_

        Args:
            ctx (commands.Context): _description_
        """

        return await _is_registered(ctx.bot, ctx.author)

    return commands.check(pred)
