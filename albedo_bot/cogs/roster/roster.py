import pprint
from typing import TYPE_CHECKING

from discord import User
from discord.ext import commands


import albedo_bot.config as config
from image_processing.processing_client import remote_compute_results
from albedo_bot.database.schema.hero import Hero, AscensionValues
from albedo_bot.utils.errors import CogCommandError
from albedo_bot.utils.message import EmbedWrapper, send_embed, send_embed_exception
from albedo_bot.cogs.roster.utils.base_roster import BaseRosterCog
from albedo_bot.database.schema.hero.hero_instance import HeroInstance, HeroInstanceData, HeroUpdateStatus


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

        author_id: int = ctx.author.id

        detected_hero_dict: dict[str, int] = {}
        detected_hero_list: list[HeroInstanceData] = []

        for image_number, attachment in enumerate(ctx.message.attachments):

            command_list = [str(attachment)]
            if config.VERBOSE:
                command_list.append("-v")
            roster_json = remote_compute_results(
                config.processing_server_address, 15000, command_list)
            if config.VERBOSE:
                pprint.pprint(roster_json.json_dict())

            for detected_index, detected_hero_data in enumerate(
                    roster_json.hero_data_list):

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
                    await send_embed_exception(
                        ctx, CogCommandError(embed_wrapper=EmbedWrapper(
                            title="Unknown Hero Detected",
                            description=(
                                "Unable to find detected hero with "
                                f"name: '{detected_hero_data.name}' in image "
                                f"{image_number}, position {detected_index}"))))
                    continue

                hero_tuple = HeroInstanceData(
                    hero_name=hero_result.name,
                    hero_id=hero_result.id,
                    signature_level=detected_hero_data.signature_item.label,
                    furniture_level=detected_hero_data.furniture.label,
                    ascension_level=AscensionValues[detected_hero_data.ascension.label],
                    engraving_level=detected_hero_data.engraving.label)

                hero_name = hero_tuple.hero_name
                if hero_name in detected_hero_dict:
                    hero_index = detected_hero_dict[hero_name]
                    detected_hero_list[hero_index] = max(
                        hero_tuple, detected_hero_list[hero_index])
                else:
                    detected_hero_dict[hero_name] = len(detected_hero_list)
                    detected_hero_list.append(hero_tuple)

        updated_hero_list: list[HeroInstanceData] = []

        for hero_tuple in detected_hero_list:
            hero_instance_select = self.db_select(HeroInstance).where(
                HeroInstance.player_id == author_id,
                HeroInstance.hero_id == hero_tuple.hero_id)

            hero_instance_result = await self.db_execute(
                hero_instance_select).first()
            new_hero_instance = HeroInstance.from_instance_tuple(
                hero_tuple, author_id)
            # New Hero
            if hero_instance_result is None:
                hero_tuple.hero_update_status = HeroUpdateStatus.NEW_HERO
                updated_hero_list.append(hero_tuple)
            # Updated hero
            elif new_hero_instance > hero_instance_result:
                hero_tuple.hero_update_status = HeroUpdateStatus.UPDATED_HERO
                updated_hero_list.append(hero_tuple)
            else:
                continue
            self.bot.session.add(new_hero_instance)

        if len(updated_hero_list) == 0:
            heroes_result_str = "No Hero updates detected"
        else:
            heroes_result_str = await self.fetch_heroes(updated_hero_list)
        await send_embed(ctx, embed_wrapper=EmbedWrapper(
            description=heroes_result_str))


def setup(bot: "AlbedoBot"):
    """_summary_

    Args:
        bot (AlbedoBot): _description_
    """
    bot.add_cog(RosterCog(bot))
