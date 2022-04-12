import pprint
from typing import Dict, List, Union, TYPE_CHECKING

from discord.ext import commands
from discord import Member

from image_processing.processing_client import remote_compute_results
from image_processing.afk.hero.hero_data import RosterJson
from sqlalchemy import select

import albedo_bot.config as config
from albedo_bot.cogs.roster.utils.roster_converters import HeroConverter
from albedo_bot.database.schema.hero import HeroInstance, Hero, AscensionValues
from albedo_bot.cogs.utils.message import send_message
from albedo_bot.database.schema.hero import (
    HeroInstance, HeroInstanceTuple, HeroList, Hero)

from albedo_bot.cogs.roster.utils.hero import(
    valid_engraving, valid_furniture, valid_signature_item, valid_ascension,
    furniture_range, engraving_range, signature_item_range)


if TYPE_CHECKING:
    from albedo_bot.bot import AlbedoBot


class Roster(commands.Cog):
    """_summary_

    Args:
        commands (_type_): _description_
    """

    def __init__(self, bot: "AlbedoBot"):
        """_summary_

        Args:
            bot (AlbedoBot): _description_
        """
        self.bot = bot
        self.hero_alias = config.hero_alias

    @bot.group(name="roster")
    async def roster_command(self, ctx: commands.Context):
        """[summary]

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        """
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid sub command passed...')

    async def _add_hero(self, ctx: commands.Context, player: Member, hero: Hero,
                        ascension: str, signature_item: int, furniture: int,
                        engraving: int):
        """[summary]

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            name (str): [description]
        """

        if not self.check_input(ctx, hero, ascension, signature_item,
                                furniture, engraving):
            return

        from sqlalchemy.orm import Session
        test: Session = None
        test.query()

        async with self.bot.session:
            hero_select = select(HeroInstance).where(
                HeroInstance.hero_id == hero.id, HeroInstance.player_id.id == player.id).first()
            hero_instance_object = await self.bot.session.execute(hero_select)
            # await self.bot.session.execute(select(HeroInstance)).filter_by(hero_id=hero.id, player_id=player.id).first()
            # hero_instance_object = self.bot.session.query(HeroInstance).filter_by(
            #     hero_id=hero.id, player_id=player.id).first()

            if hero_instance_object is None:
                hero_instance_object = HeroInstance()
                hero_instance_object.player_id = player.id
                hero_instance_object.hero_id = hero.id
            hero_instance_object.ascension_level = ascension
            hero_instance_object.signature_level = signature_item
            hero_instance_object.furniture_level = furniture
            hero_instance_object.engraving_level = engraving

            await self.bot.session.add(hero_instance_object)

        hero_message = self.fetch_heroes([hero_instance_object])
        await send_message(ctx, hero_message)

    def check_input(self, ctx: commands.Context, hero: Hero, ascension: Union[str, int],
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

    async def fetch_heroes(self, hero_list: List[HeroInstance]):
        """_summary_

        Args:
            hero_list (List[HeroInstance]): _description_
        """
        hero_result = []
        async with self.bot.session:
            for hero_instance in hero_list:
                hero_select = select(Hero).where(
                    Hero.id == hero_instance.hero_id)
                hero_object = await self.bot.session.execute(hero_select).first()
                hero_tuple = HeroInstanceTuple(hero_object.name, hero_instance.hero_id,
                                               hero_instance.signature_level,
                                               hero_instance.furniture_level,
                                               hero_instance.ascension_level.name,
                                               hero_instance.engraving_level)
                hero_result.append(hero_tuple)
        heroes_message_object = HeroList(hero_result)
        output = str(heroes_message_object)
        return output

    def fetch_heroes_embed(self, hero_list: List[HeroInstance]):
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

        return heroes_message_object.generate_embed()

    def fetch_roster(self, discord_id: int):
        """_summary_

        Args:
            discord_id (int): _description_
        """

        roster_results = GV.session.query(HeroInstance).filter_by(
            player_id=discord_id).all()
        return fetch_heroes(roster_results)

    @roster_command.command(name="show", aliases=["list"])
    async def show(self, ctx: commands.Context):
        """[summary]

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            name (str): [description]
        """

        heroes_result = fetch_roster(ctx.author.id)
        await send_message(ctx, heroes_result)

    @roster_command.command(name="add", aliases=["update"])
    async def add_hero(self, ctx: commands.Context, hero: HeroConverter,
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

    async def send_debug_hero(self, ctx: commands.Context, json_dict: Dict):
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
    async def upload(self, ctx: commands.Context):
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
