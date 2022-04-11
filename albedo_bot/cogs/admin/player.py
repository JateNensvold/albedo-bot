from discord.ext.commands.context import Context
from discord import Role

from albedo_bot.commands.helpers.player import delete_player, register_player
from albedo_bot.commands.helpers.permissions import has_permission
from albedo_bot.commands.helpers.converter import MemberConverter


from albedo_bot.commands.admin.base import admin


@admin.group(name="player")
async def player_command(ctx: Context):
    """[summary]

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
    """
    if ctx.invoked_subcommand is None:
        await ctx.send('Invalid sub command passed...')


@player_command.command(name="delete", aliases=["remove"])
@has_permission("manager")
async def delete(ctx: Context, guild_member: MemberConverter):
    """[summary]

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
    """
    await delete_player(ctx, guild_member)


@player_command.command(name="add", aliases=["register"])
@has_permission("manager")
async def add(ctx: Context,  guild_member: MemberConverter, guild_role: Role):
    """[summary]

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
    """
    await register_player(ctx, guild_member, guild_role)
