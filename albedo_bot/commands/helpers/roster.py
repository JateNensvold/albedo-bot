from typing import List, Union

from discord.ext.commands.context import Context
from discord import Member

import albedo_bot.global_values as GV
from albedo_bot.global_values import bot
from albedo_bot.schema.hero.hero_instance import (
    HeroInstance, HeroInstanceTuple, HeroList)
from albedo_bot.schema.hero import Hero
from albedo_bot.commands.helpers.hero import (
    valid_engraving, valid_furniture, valid_signature_item, valid_ascension,
    furniture_range, engraving_range, signature_item_range)
from albedo_bot.commands.helpers.utils import send_css_message

@bot.group(name="roster")
async def roster_command(ctx: Context):
    """[summary]

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
    """
    if ctx.invoked_subcommand is None:
        await ctx.send('Invalid sub command passed...')


async def _add_hero(ctx: Context, player: Member, hero: Hero,
                    ascension: str, signature_item: int, furniture: int,
                    engraving: int):
    """[summary]

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
        name (str): [description]
    """

    if not check_input(ctx, hero, ascension, signature_item,
                       furniture, engraving):
        return

    hero_instance_object = GV.session.query(HeroInstance).filter_by(
        hero_id=hero.id, player_id=player.id).first()
    if hero_instance_object is None:
        hero_instance_object = HeroInstance()
        hero_instance_object.player_id = player.id
        hero_instance_object.hero_id = hero.id
    hero_instance_object.ascension_level = ascension
    hero_instance_object.signature_level = signature_item
    hero_instance_object.furniture_level = furniture
    hero_instance_object.engraving_level = engraving
    GV.session.add(hero_instance_object)

    hero_message = fetch_heroes([hero_instance_object])
    await send_css_message(ctx, hero_message)


def check_input(ctx: Context, hero: Hero, ascension: Union[str, int],
                signature_item: int, furniture: int, engraving: int):
    """_summary_

    Args:
        ctx (Context): _description_
        hero (Hero): _description_
        ascension (Union[str, int]): _description_
        signature_item (int): _description_
        furniture (int): _description_
        engraving (int): _description_

    Returns:
        _type_: _description_
    """
    if not valid_ascension(ascension):
        ctx.send(
            f"The provided ascension value({ascension}) is not valid, "
            f"valid ascension values are ({signature_item_range(hero)}")
        return False
    if not valid_signature_item(hero, signature_item):
        ctx.send(
            f"The provided SI value({furniture}) is not valid for {hero.name}"
            f"({signature_item_range(hero)}")
        return False
    if not valid_furniture(hero, furniture):
        ctx.send(
            f"The provided furniture value({furniture}) is not valid for "
            f"{hero.name}({furniture_range(hero)}")
        return False
    if not valid_engraving(hero, engraving):
        ctx.send(
            f"The provided engraving value({furniture}) is not valid for "
            f"{hero.name}({engraving_range(hero)}")
        return False
    return True


def fetch_heroes(hero_list: List[HeroInstance]):
    """_summary_

    Args:
        hero_list (List[HeroInstance]): _description_
    """
    hero_result = []

    for hero_instance in hero_list:
        hero_object = GV.session.query(Hero).filter_by(
            id=hero_instance.hero_id).first()
        hero_tuple = HeroInstanceTuple(hero_object.name, hero_instance.hero_id,
                                       hero_instance.signature_level,
                                       hero_instance.furniture_level,
                                       hero_instance.ascension_level.name,
                                       hero_instance.engraving_level)
        hero_result.append(hero_tuple)
    heroes_message_object = HeroList(hero_result)
    output = str(heroes_message_object)
    return output


def fetch_roster(discord_id: int):
    """_summary_

    Args:
        discord_id (int): _description_
    """

    roster_results = GV.session.query(HeroInstance).filter_by(
        player_id=discord_id).all()
    return fetch_heroes(roster_results)
