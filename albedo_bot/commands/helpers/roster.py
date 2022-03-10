from typing import List
from albedo_bot.global_values import bot
from discord.ext.commands.context import Context

import albedo_bot.global_values as GV
from albedo_bot.schema.hero.hero_instance import (
    HeroInstance, HeroInstanceTuple, HeroList)
from albedo_bot.schema.hero import Hero

@bot.group(name="roster")
async def roster_command(ctx: Context):
    """[summary]

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
    """
    if ctx.invoked_subcommand is None:
        await ctx.send('Invalid sub command passed...')


def check_input(hero: Hero, ascension: str, signature_item: int,
                furniture: int, engraving: int):
    """_summary_

    Args:
        hero (Hero): _description_
        ascension (str): _description_
        signature_item (int): _description_
        furniture (int): _description_
        engraving (int): _description_
    """
    

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
                                       hero_instance.ascension_level,
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
