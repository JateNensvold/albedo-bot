from discord.ext.commands.context import Context

from albedo_bot.commands.helpers.converter import HeroConverter
from albedo_bot.commands.helpers.roster import (
    roster_command, fetch_roster, _add_hero)


@roster_command.command(name="show", aliases=["list"])
async def show(ctx: Context):
    """[summary]

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
        name (str): [description]
    """

    heroes_result = fetch_roster(ctx.author.id)
    await ctx.send(heroes_result)


@roster_command.command(name="add", aliases=["update"])
async def add_hero(ctx: Context, hero: HeroConverter,
                   ascension: str, signature_item: int, furniture: int,
                   engraving: int):
    """[summary]

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
        name (str): [description]
    """
    await _add_hero(ctx, ctx.author, hero, ascension, signature_item, furniture,
              engraving)
