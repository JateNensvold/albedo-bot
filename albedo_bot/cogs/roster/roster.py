import pprint
from typing import List, TYPE_CHECKING
from time import time

from discord import User
from discord.ext import commands


import albedo_bot.config as config
from image_processing.processing_client import remote_compute_results
from albedo_bot.database.schema.hero import Hero, AscensionValues
from albedo_bot.utils.message import EmbedWrapper, send_embed
from albedo_bot.cogs.roster.utils.base_roster import BaseRosterCog
from albedo_bot.database.schema.hero.hero_instance import HeroInstanceTuple


if TYPE_CHECKING:
    from albedo_bot.bot import AlbedoBot


class RosterCog(BaseRosterCog):
    """
    A group of commands used to manager a players AFK Arena roster
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
        """
        A group of commands used to manager a players AFK Arena roster

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        """

    @roster.command(name="show", aliases=["list"])
    async def show(self, ctx: commands.Context, guild_member: User = None):
        """
        Shows a players roster

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            guild_member (User, optional): User name, user mention, or user ID to show
                the roster of . Defaults to showing the roster of whoever
                invoked the command when no user is provided.
        """

        user_id = ctx.author.id
        if guild_member:
            user_id = guild_member.id

        heroes_result = await self.fetch_roster(user_id)
        await send_embed(ctx, embed_wrapper=EmbedWrapper(
            description=heroes_result))

    @roster.command(name="add", aliases=["update"])
    async def _add(self, ctx: commands.Context, hero: Hero,
                   ascension: str, signature_item: int, furniture: int,
                   engraving: int):
        """
        Add a AFK Arena hero to your roster

        Args:
            ctx (commands.Context): ctx (Context): invocation context
                containing information on how a discord event/command was
                invoked
            hero (Hero): Name or hero ID of hero to add
            ascension (str): Ascension level of hero
            signature_item (int): SI level of hero
            furniture (int): Furniture level of hero
            engraving (int): Engraving level of hero
        """
        await self.add_hero(ctx, ctx.author, hero, ascension, signature_item, furniture,
                            engraving)

    @roster.command(name="upload")
    async def upload(self, ctx: commands.Context):
        """
        Automatically detects the investment levels for all heroes in
        roster screenshots attached to this command

        Args:
            ctx (commands.Context): ctx (Context): invocation context
                containing information on how a discord event/command was
                invoked
        """

        author_id = ctx.author.id

        for attachment in ctx.message.attachments:

            command_list = [str(attachment)]
            if config.VERBOSE:
                command_list.append("-v")
            roster_json = remote_compute_results(
                config.processing_server_address, 15000, command_list)
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
            await send_embed(ctx, embed_wrapper=EmbedWrapper(
                description=heroes_result))

            # await send_message(ctx,
            #                    heroes_result,
            #                    css=False)


def setup(bot: "AlbedoBot"):
    """_summary_

    Args:
        bot (AlbedoBot): _description_
    """
    bot.add_cog(RosterCog(bot))
