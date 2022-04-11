from discord.ext.commands.context import Context

from albedo_bot.commands.helpers.permissions import has_permission
from albedo_bot.global_values import bot


@bot.group(name="admin")
@has_permission("guild_manager")
async def admin(ctx: Context):
    """
    Group of commands for all tasks that require some higher level of permissions.
    All commands require either' guild manager', 'manager' or 'admin' and higher to run

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
    """
    if ctx.invoked_subcommand is None:
        await ctx.send('Invalid sub command passed...')
