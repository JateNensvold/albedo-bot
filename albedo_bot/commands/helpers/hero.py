
from discord.ext.commands.context import Context
from albedo_bot.commands.base import bot, session
from albedo_bot.schema import Hero


@bot.group()
async def hero(ctx: Context):
    """[summary]

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
    """
    if ctx.invoked_subcommand is None:
        await ctx.send('Invalid sub command passed...')


async def _find_hero(ctx: Context, hero_name):
    """
    Search for a hero with the name 'hero_name' in the database. Return true if
    there is a match, return False otherwise

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
        hero_name ([type]): name of hero to look for

    Returns:
        [type]: Return True if 'hero_name' is found in the heroes table,
            False otherwise
    """
    hero_result = session.query(Hero).filter_by(
        name=hero_name).first()
    if hero_result is not None:
        ctx.send(
            f"A hero with the name {hero_name} has already been registered "
            f"'{hero_result}'")
        return True
    return False


async def _add_hero(ctx: Context, hero_name: str):
    """[summary]

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
        hero_name (str): [description]
    """
    if not _find_hero(ctx, hero_name):
        new_hero = Hero(name=hero_name)
        session.add(new_hero)
        await ctx.send(f"Added new hero {hero_name} as '{new_hero}'")
