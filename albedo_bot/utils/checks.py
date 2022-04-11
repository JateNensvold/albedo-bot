

from discord.ext import commands

from albedo_bot.commands.utils.permissions import Permissions

import albedo_bot.global_values as GV


def _check_permission(ctx: commands.Context, config_role_name: str,
                      permissions: Permissions):
    """
    Decorator helper that performs permissions checks and accepts the
    parameters that will get passed to the decorated function

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
    """

    required_permission = permissions.permission_name_lookup(
        config_role_name.lower())

    return permissions.lookup(ctx.author) >= required_permission


def check_config_permission(config_role_name: str):
    """_summary_

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
        return _check_permission(ctx, config_role_name, GV.PERMISSIONS_DATA)
    return commands.check(pred)
