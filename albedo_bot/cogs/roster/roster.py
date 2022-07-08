import pprint
from typing import List, TYPE_CHECKING

from discord.ext import commands

from image_processing.processing_client import remote_compute_results

import albedo_bot.config as config
from albedo_bot.database.schema.hero import Hero, AscensionValues
from albedo_bot.utils.message import EmbedField, EmbedWrapper, send_embed, send_message
from albedo_bot.cogs.roster.utils.base_roster import BaseRosterCog
from albedo_bot.database.schema.hero.hero_instance import HeroInstanceTuple


if TYPE_CHECKING:
    from albedo_bot.bot import AlbedoBot


class RosterCog(BaseRosterCog):
    """
    [summary]

    Args:
        commands (_type_): _description_
    """

    def __init__(self, bot: "AlbedoBot"):
        """_summary_

        Args:
            bot (AlbedoBot): _description_
        """
        super().__init__(bot)
        self.hero_alias = config.hero_alias

    @commands.group(name="roster")
    async def roster(self, ctx: commands.Context):
        """[summary]

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        """
        # await self.send_help(ctx)
        # if ctx.invoked_subcommand is None:
        #     await ctx.send('Invalid sub command passed...')

    # def fetch_heroes_embed(self, hero_list: List[HeroInstance]):
    #     """_summary_

    #     Args:
    #         hero_list (List[HeroInstance]): _description_
    #     """
    #     hero_result = []

    #     for hero_instance in hero_list:
    #         hero_object = GV.session.query(Hero).filter_by(
    #             id=hero_instance.hero_id).first()
    #         hero_tuple = HeroInstanceTuple(hero_object.name, hero_instance.hero_id,
    #                                        hero_instance.signature_level,
    #                                        hero_instance.furniture_level,
    #                                        hero_instance.ascension_level.name,
    #                                        hero_instance.engraving_level)
    #         hero_result.append(hero_tuple)
    #     heroes_message_object = HeroList(hero_result)

    #     return heroes_message_object.generate_embed()

    @roster.command(name="show", aliases=["list"])
    async def show(self, ctx: commands.Context):
        """[summary]

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            name (str): [description]
        """

        heroes_result = await self.fetch_roster(ctx.author.id)
        await send_embed(ctx, embed_wrapper=EmbedWrapper(
            description=heroes_result))

    @roster.command(name="add", aliases=["update"])
    async def _add(self, ctx: commands.Context, hero: Hero,
                   ascension: str, signature_item: int, furniture: int,
                   engraving: int):
        """[summary]

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            name (str): [description]
        """
        await self.add_hero(ctx, ctx.author, hero, ascension, signature_item, furniture,
                            engraving)

    # async def send_debug_hero(self, ctx: commands.Context, json_dict: Dict):
    #     """_summary_

    #     Args:
    #         ctx (Context): _description_
    #         json_dict (Dict): _description_
    #     """
    #     dict_message = pprint.pformat(json_dict, width=200)
    #     start_message = 0
    #     print(dict_message)
    #     while start_message < len(dict_message):
    #         await ctx.send(f"```\n{dict_message[start_message:start_message+1991]}\n```")
    #         start_message += 1991

    @roster.command(name="upload")
    async def upload(self, ctx: commands.Context):
        """_summary_

        Args:
            ctx (Context): _description_
        """

        address = "tcp://localhost:5555"

        author_id = ctx.author.id

        for attachment in ctx.message.attachments:

            command_list = [str(attachment)]
            if config.VERBOSE:
                command_list.append("-v")
            roster_json = remote_compute_results(
                address, 15000, command_list)
            if config.VERBOSE:
                pprint.pprint(roster_json.json_dict())

            hero_tuple_list: List[HeroInstanceTuple] = []
            for detected_index, detected_hero_data in enumerate(roster_json.hero_data_list):

                if detected_hero_data.name in self.hero_alias:

                    hero_database_name = self.hero_alias.get(
                        detected_hero_data.name)

                    hero_select = self.db_select(Hero).where(
                        Hero.name == hero_database_name)

                    hero_result = await self.db_execute(hero_select).first()

                else:
                    hero_select = self.db_select(Hero).where(
                        Hero.name.ilike(f"{detected_hero_data.name}%"))
                    hero_result = await self.db_execute(hero_select).first()
                if not hero_result:
                    await ctx.send(
                        "Unable to find detected hero with name: "
                        f"'{detected_hero_data.name}' in position {detected_index}")
                    continue

                hero_tuple = HeroInstanceTuple(
                    hero_name=hero_result.name,
                    hero_id=hero_result.id,
                    signature_level=detected_hero_data.signature_item.label,
                    furniture_level=detected_hero_data.furniture.label,
                    ascension_level=AscensionValues[detected_hero_data.ascension.label],
                    engraving_level=detected_hero_data.engraving.label)
                hero_tuple_list.append(hero_tuple)

                # hero_instance_select = self.db_select(HeroInstance).where(
                #     HeroInstance.player_id == author_id, HeroInstance.hero_id == hero_result.id)

                # hero_instance_result = await self.db_execute(hero_instance_select).first()

            # hero_update = True
            # if hero_instance_result is None:
            #     hero_instance_result = HeroInstance(
            #         hero_id=hero_result.id, player_id=author_id,
            #         signature_level=detected_hero_data.signature_item.label,
            #         furniture_level=detected_hero_data.furniture.label,
            #         ascension_level=AscensionValues[detected_hero_data.ascension.label],
            #         engraving_level=detected_hero_data.engraving.label)
            # else:
            #     hero_update = hero_instance_result.update(
            #         detected_hero_data.signature_item.label,
            #         detected_hero_data.furniture.label,
            #         detected_hero_data.ascension.label,
            #         detected_hero_data.engraving.label)
            # if hero_update:
            #     self.bot.session.add(hero_instance_result)
            heroes_result = await self.fetch_heroes(hero_tuple_list)
            await send_embed(ctx, embedWrapper=EmbedWrapper(
                description=heroes_result))

            await send_message(ctx,
                               heroes_result,
                               css=False)
            # await ctx.send(embed=fetch_heroes_embed(hero_instance_list))


def setup(bot: "AlbedoBot"):
    """_summary_

    Args:
        bot (AlbedoBot): _description_
    """
    bot.add_cog(RosterCog(bot))
