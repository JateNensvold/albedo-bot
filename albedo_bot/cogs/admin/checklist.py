from discord.ext.commands.context import Context
from albedo_bot.commands.admin.base import admin

from albedo_bot.commands.helpers.permissions import has_permission
from albedo_bot.commands.helpers.checklist import (
    _add_hero, _remove_hero, _add_checklist, _remove_checklist)


@admin.group(name="checklist")
async def checklist_command(ctx: Context):
    """[summary]

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
    """
    if ctx.invoked_subcommand is None:
        await ctx.send('Invalid sub command passed...')


# @admin.group(name="checklist hero")
# async def checklist_hero_command(ctx: Context):
#     """[summary]

#     Args:
#         ctx (Context): invocation context containing information on how
#             a discord event/command was invoked
#     """
#     if ctx.invoked_subcommand is None:
#         await ctx.send('Invalid sub command passed...')


@checklist_command.command(name="add", aliases=["update"])
@has_permission("guild_manager")
async def add_hero(ctx: Context, checklist_name: str, hero_name: str,
                   ascension: int,  signature: int, furniture: int,
                   engraving: int):
    """_summary_

    Args:
        ctx (Context): _description_
        checklist_name (str): _description_
        hero_name (str): _description_
        ascension (int): _description_
        signature (int): _description_
        furniture (int): _description_
        engraving (int): _description_
    """
    await _add_hero(ctx, checklist_name, hero_name,
                    ascension, signature, furniture, engraving)


@checklist_command.command(name="remove")
@has_permission("guild_manager")
async def remove_hero(ctx: Context, checklist_name: str, hero_name: str):
    """_summary_

    Args:
        ctx (Context): _description_
        checklist_name (str): _description_
        hero_name (str): _description_
    """
    await _remove_hero(ctx, checklist_name, hero_name)


@checklist_command.command(name="create", aliases=["register"])
@has_permission("guild_manager")
async def add_checklist(ctx: Context, checklist_name: str, description: str):
    """_summary_

    Args:
        ctx (Context): _description_
        checklist_name (str): _description_
    """
    await _add_checklist(ctx, checklist_name, description)


@checklist_command.command(name="delete")
@has_permission("guild_manager")
async def remove_checklist(ctx: Context, checklist_name: str):
    """_summary_

    Args:
        ctx (Context): _description_
        checklist_name (str): _description_
    """
    await _remove_checklist(ctx, checklist_name)
