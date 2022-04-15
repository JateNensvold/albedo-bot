

from discord.ext import commands

import albedo_bot.config as config


def _check_permission(ctx: commands.Context, config_role_name: str):
    """
    Lookup if the author of a message has equal or higher permissions than the
        permissions assigned to 'config_role_name'

    Args:
        ctx (commands.Context): invocation context containing information on how
            a discord event/command was invoked
        config_role_name (str): name of role in permissions config file

    Returns:
        bool: True if the author has the required permissions level,
            False otherwise
    """
    required_permission = config.permissions.permission_name_lookup[
        config_role_name.lower()]

    return config.permissions.lookup(ctx.author) >= required_permission


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
        return _check_permission(ctx, config_role_name)
    return commands.check(pred)
