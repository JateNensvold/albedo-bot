

from discord.ext.commands.context import Context

import albedo_bot.global_values as GV
from albedo_bot.schema.hero import HeroInstance
from albedo_bot.commands.helpers.converter import HeroConverter
from albedo_bot.commands.helpers.roster import (
    roster_command, fetch_roster, fetch_heroes)


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
                   ascension: str, signature_item: int, furniture: int, engraving: int):
    """[summary]

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
        name (str): [description]
    """

    hero_instance_object = GV.session.query(HeroInstance).filter_by(
        hero_id=hero.id).first()
    hero_instance_object.ascension_level = ascension
    hero_instance_object.signature_level = signature_item
    hero_instance_object.furniture_level = furniture
    hero_instance_object.engraving_level = engraving
    GV.session.add(hero_instance_object)

    hero_message = fetch_heroes([hero_instance_object])
    await ctx.send(hero_message)
