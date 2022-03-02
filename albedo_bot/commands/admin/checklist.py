from discord.ext.commands.context import Context
from albedo_bot.commands.admin.base import admin

from albedo_bot.commands.helpers.permissions import has_permission


@admin.group(name="checklist")
async def checklist_command(ctx: Context):
    """[summary]

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
    """
    if ctx.invoked_subcommand is None:
        await ctx.send('Invalid sub command passed...')


@checklist_command.command(name="register", aliases=["add"])
@has_permission("guild_manager")
async def register(ctx: Context, hero_name: str):
    """[summary]

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
        name (str): [description]
    """
    await _add_hero(ctx, hero_name)
