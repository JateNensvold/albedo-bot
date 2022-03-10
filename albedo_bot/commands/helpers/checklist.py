from discord.ext.commands.context import Context
import albedo_bot.global_values as GV
from albedo_bot.global_values import bot
from albedo_bot.commands.helpers.hero import missing_hero_message
from albedo_bot.schema import Hero
from albedo_bot.schema.checklist import Checklist, ChecklistHero


@bot.group(name="checklist")
async def checklist_command(ctx: Context):
    """
    Grouping for guild subcommands


    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
    """

    if ctx.invoked_subcommand is None:
        await ctx.send('Invalid sub command passed...')


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
    joined_result = "\n".join([str(checklist_object)
                              for checklist_object in checklist_result])
    await ctx.send(f"```\n{joined_result}\n```")


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


async def _add_hero(ctx: Context, checklist_name: str, hero_name: str,
                    ascension: int,  signature: int, furniture: int,
                    engraving: int):
    """_summary_

    Args:
        checklist_name (str): _description_
        hero_name (str): _description_
    """

    checklist_hero_object = await _check_input(ctx, checklist_name, hero_name)
    hero_object = GV.session.query(Hero).filter_by(
        name=hero_name).first()
    if hero_object is None:
        return
    if checklist_hero_object is None:
        #         signature_level = Column(Integer)
        # furniture_level = Column(Integer)
        # ascension_level = Column(Integer)
        # engraving_level = Column(Integer)
        checklist_hero_object = ChecklistHero(
            checklist_name=checklist_name, hero_name=hero_name,
            signature_level=signature, furniture_level=furniture,
            ascension_level=ascension, engraving_level=engraving)
        await ctx.send(
            f"Successfully added `{hero_name}` to `{checklist_name}` as "
            f"`{checklist_hero_object}`")
    else:
        checklist_hero_object.ascension_level = ascension
        checklist_hero_object.signature_level = signature
        checklist_hero_object.furniture_level = furniture
        checklist_hero_object.engraving_level = engraving

        await ctx.send(
            f"Successfully updated `{hero_name}` in `{checklist_name}` to "
            f"`{checklist_hero_object}`")
    GV.session.add(checklist_hero_object)


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
    else:
        GV.session.delete(checklist_hero_object)
        await ctx.send(
            f"Successfully removed `{hero_name}` from `{checklist_name}`")


async def _add_checklist(ctx: Context, checklist_name: str, description: str):
    """_summary_

    Args:
        checklist_name (str): _description_
        description (str): _description_
    """
    checklist_object = GV.session.query(Checklist).filter_by(
        name=checklist_name).first()
    if checklist_object is None:
        new_checklist = Checklist(name=checklist_name, description=description)
        GV.session.add(new_checklist)
        await ctx.send(
            f"Checklist with name `{checklist_name}` has been created")
    else:
        await ctx.send(f"Checklist with name `{checklist_name}` already exists")


async def _remove_checklist(ctx: Context, checklist_name: str):
    """_summary_

    Args:
        checklist_name (str): _description_
    """
    checklist_object = GV.session.query(Checklist).filter_by(
        name=checklist_name).first()

    if checklist_object is not None:
        GV.session.delete(checklist_object)
        await ctx.send(f"Successfully removed checklist `{checklist_name}`")
    else:
        await missing_checklist_message(ctx, checklist_name)
