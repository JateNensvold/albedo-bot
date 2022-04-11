import pprint
from typing import Dict, List, Union

from discord.ext.commands.context import Context
from image_processing.processing_client import remote_compute_results
from image_processing.afk.hero.hero_data import RosterJson

import albedo_bot.global_values as GV
from albedo_bot.commands.helpers.converter import HeroConverter
from albedo_bot.schema.hero import HeroInstance, Hero
from albedo_bot.schema.hero.hero_instance import AscensionValues
from albedo_bot.commands.helpers.roster import (
    fetch_heroes_embed, roster_command, fetch_roster, _add_hero, fetch_heroes)
from albedo_bot.global_values import bot
from albedo_bot.commands.helpers.utils import send_message


@bot.group(name="ping")
async def ping_command(ctx: Context):
    """[summary]

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
    """
    await ctx.send("pong")
    # if ctx.invoked_subcommand is None:
    #     await ctx.send('Invalid sub command passed...')


@roster_command.command(name="show", aliases=["list"])
async def show(ctx: Context):
    """[summary]

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
        name (str): [description]
    """

    heroes_result = fetch_roster(ctx.author.id)
    await send_message(ctx, heroes_result)


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


async def send_debug_hero(ctx: Context, json_dict: Dict):
    """_summary_

    Args:
        ctx (Context): _description_
        json_dict (Dict): _description_
    """
    dict_message = pprint.pformat(json_dict, width=200)
    start_message = 0
    print(dict_message)
    while start_message < len(dict_message):
        await ctx.send(f"```\n{dict_message[start_message:start_message+1991]}\n```")
        start_message += 1991


@roster_command.command(name="upload")
async def upload(ctx: Context):
    """_summary_

    Args:
        ctx (Context): _description_
    """

    address = "tcp://localhost:5555"

    author_id = ctx.author.id

    for attachment in ctx.message.attachments:

        command_list = [str(attachment)]
        if GV.VERBOSE:
            command_list.append("-v")
        json_dict = remote_compute_results(
            address, 15000, command_list)
        if GV.VERBOSE:
            pprint.pprint(json_dict)

        detected_roster = RosterJson.from_json(json_dict)
        hero_instance_list: List[HeroInstance] = []
        for detected_index, detected_hero_data in enumerate(detected_roster.hero_data_list):
            if detected_hero_data.name in GV.HERO_ALIAS:
                hero_database_name = GV.HERO_ALIAS[detected_hero_data.name]
                reference_hero = GV.session.query(Hero).filter_by(
                    name=hero_database_name).first()
            else:
                reference_hero = GV.session.query(Hero).filter(
                    Hero.name.ilike(f"{detected_hero_data.name}%")).first()
            if not reference_hero:
                await ctx.send(
                    "Unable to find detected hero with name: "
                    f"{detected_hero_data.name} in position {detected_index}")
                continue

            hero_instance: Union[HeroInstance, None] = GV.session.query(
                HeroInstance).filter_by(player_id=author_id,
                                        hero_id=reference_hero.id).first()

            hero_update = True
            if hero_instance is None:
                hero_instance = HeroInstance(
                    hero_id=reference_hero.id, player_id=author_id,
                    signature_level=detected_hero_data.signature_item.label,
                    furniture_level=detected_hero_data.furniture.label,
                    ascension_level=AscensionValues[detected_hero_data.ascension.label],
                    engraving_level=detected_hero_data.engraving.label)
            else:
                hero_update = hero_instance.update(
                    detected_hero_data.signature_item.label,
                    detected_hero_data.furniture.label,
                    detected_hero_data.ascension.label,
                    detected_hero_data.engraving.label)
            if hero_update:
                GV.session.add(hero_instance)
            hero_instance_list.append(hero_instance)
        await send_message(ctx, f"{str(ctx.author)}\n {fetch_heroes(hero_instance_list)}", css=False)
        # await ctx.send(embed=fetch_heroes_embed(hero_instance_list))
