from discord.ext.commands.context import Context

import albedo_bot.global_values as GV
from albedo_bot.commands.helpers.hero import hero_command
from albedo_bot.schema import Hero


@hero_command.command(name="list")
async def hero_list(ctx: Context):
    """[summary]

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
        name (str): [description]
    """

    heroes_result = GV.session.query(Hero).all()

    await ctx.send("\n".join(
        [f"`{hero_object}`" for hero_object in heroes_result]))
