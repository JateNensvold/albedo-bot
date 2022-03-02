from discord.ext.commands.context import Context
from albedo_bot.global_values import bot
import albedo_bot.global_values as GV
from albedo_bot.schema import Hero


async def missing_hero_message(ctx: Context, hero_name: str):
    """_summary_

    Args:
        ctx (Context): _description_
        checklist_name (str): _description_
    """
    await ctx.send(
        f"A hero with the name `{hero_name}` was unable to be found in the "
        "hero database")

@bot.group(name="hero")
async def hero_command(ctx: Context):
    """[summary]

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
    """
    if ctx.invoked_subcommand is None:
        await ctx.send('Invalid sub command passed...')


async def _find_hero(hero_name):
    """
    Search for a hero with the name 'hero_name' in the database. Return true if
    there is a match, return False otherwise

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
        hero_name ([type]): name of hero to look for

    Returns:
        [type]: Return 'hero_object' if found in the heroes table,
            None otherwise
    """
    hero_result = GV.session.query(Hero).filter_by(
        name=hero_name).first()
    return hero_result


async def _add_hero(ctx: Context, hero_name: str):
    """[summary]

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
        hero_name (str): [description]
    """
    hero_object = await _find_hero(hero_name)
    if hero_object is None:
        new_hero = Hero(name=hero_name)
        GV.session.add(new_hero)
        await ctx.send(f"Added new hero `{hero_name}` as `{new_hero}`")
    else:
        await ctx.send(
            f"A hero with the name `{hero_name}` has already been registered "
            f"`{hero_object}`")


async def _remove_hero(ctx: Context, hero_name: str):
    """_summary_

    Args:
        ctx (Context): _description_
        hero_name (str): _description_
    """
    hero_result = await _find_hero(hero_name)
    if hero_result:
        GV.session.delete(hero_result)
        await ctx.send(f"Removed hero `{hero_result}` from hero database")
    else:
        await missing_hero_message(ctx, hero_name)