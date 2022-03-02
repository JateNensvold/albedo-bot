from discord.ext.commands.context import Context
import albedo_bot.global_values as GV

from albedo_bot.commands.helpers.hero import missing_hero_message
from albedo_bot.schema import Hero
from albedo_bot.schema.checklist import Checklist, ChecklistHero


async def missing_checklist_message(ctx: Context, checklist_name: str):
    """_summary_

    Args:
        ctx (Context): _description_
        checklist_name (str): _description_
    """
    await ctx.send(
        f"Unable to find a checklist with the name `{checklist_name}`")


async def _list_checklist():
    """
    List all checklist's currently in database
    """

    checklist_objects = GV.session.query(Checklist).all()
    return checklist_objects


async def show_checklist(ctx: Context, checklist_name: str):
    """_summary_

    Args:
        ctx (Context): _description_
        checklist_name (str): _description_
    """
    checklist_object = GV.session.query(Checklist).filter_by(
        name=checklist_name).first()
    if checklist_object is None:
        await missing_checklist_message(ctx, checklist_name)
        return

    checklist_result = await _show_checklist(checklist_name)
    joined_result = "\n".join(checklist_result)
    await ctx.send(f"```{joined_result}```")


async def _show_checklist(checklist_name: str):
    """
    Get all heroes currently in checklist with name `checklist_name`

    Args:
        checklist_name (str): _description_
    """

    checklist_heroes = GV.session.query(ChecklistHero).filter_by(
        checklist_name=checklist_name).all()
    return checklist_heroes


async def _check_input(ctx: Context, checklist_name: str, hero_name: str):
    """_summary_

    Args:
        ctx (Context): _description_
        checklist_name (str): _description_
        hero_name (str): _description_

    Returns:
        _type_: _description_
    """
    checklist_object = GV.session.query(Checklist).filter_by(
        name=checklist_name).first()
    if checklist_object is None:
        await missing_checklist_message(ctx, checklist_name)
        return None

    hero_object = GV.session.query(Hero).filter_by(
        name=hero_name).first()
    if hero_object is None:
        await missing_hero_message(ctx, hero_name)
        return None

    checklist_hero_object = GV.session.query(ChecklistHero).filter_by(
        checklist_name=checklist_name, hero_name=hero_name).first()
    return checklist_hero_object


async def _add_hero(ctx: Context, checklist_name: str, hero_name: str):
    """_summary_

    Args:
        checklist_name (str): _description_
        hero_name (str): _description_
    """

    checklist_hero_object = await _check_input(ctx, checklist_name, hero_name)
    if checklist_hero_object is not None:
        return

    if checklist_hero_object is None:

        new_checklist_hero = ChecklistHero(checklist_name=checklist_name,
                                           hero_name=hero_name)
        GV.session.add(new_checklist_hero)
        await ctx.send(f"Successfully added `{hero_name}` to `{checklist_name}`")
    else:
        await ctx.send(
            f"Checklist `{checklist_name}` already contains a hero with the "
            f"name `{hero_name}`")


async def _remove_hero(ctx: Context, checklist_name: str, hero_name: str):
    """_summary_

    Args:
        checklist_name (str): _description_
        hero_name (str): _description_
    """
    checklist_hero_object = await _check_input(ctx, checklist_name, hero_name)
    if checklist_hero_object is None:
        await ctx.send(
            f"Checklist `{checklist_name}` does not contain a hero with the "
            f"name `{hero_name}`")
        return

    GV.session.delete(checklist_hero_object)
    await ctx.send(
        f"Successfully removed `{hero_name}` from `{checklist_name}`")


async def _add_checklist(ctx: Context, checklist_name: str, description: str):
    """_summary_

    Args:
        checklist_name (str): _description_
        description (str): _description_
    """


async def _remove_checklist(ctx: Context, checklist_name: str):
    """_summary_

    Args:
        checklist_name (str): _description_
    """
