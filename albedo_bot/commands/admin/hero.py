from discord.ext.commands.context import Context
from albedo_bot.commands.helpers.hero import hero, _add_hero
from albedo_bot.commands.helpers.permissions import has_permission

@hero.command(name="register", aliases=["add"])
@has_permission(100)
async def register(ctx: Context, hero_name: str):
    """[summary]

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
        name (str): [description]
    """
    _add_hero(ctx, hero_name)
