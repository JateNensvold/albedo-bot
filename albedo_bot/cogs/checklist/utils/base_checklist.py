
from discord.ext import commands
from discord import User

from albedo_bot.cogs.utils.base_cog import BaseCog
from albedo_bot.database.schema.checklist import Checklist, ChecklistHero
from albedo_bot.utils.errors import CogCommandError
from albedo_bot.utils.message import EmbedWrapper, send_embed
from albedo_bot.cogs.hero.utils.converter.ascension import AscensionValue
from albedo_bot.cogs.hero.utils.converter.engraving import EngravingValue
from albedo_bot.cogs.hero.utils.converter.furniture import FurnitureValue
from albedo_bot.cogs.hero.utils.converter.signature_item import (
    SignatureItemValue)
from albedo_bot.database.schema.hero.hero import Hero
from albedo_bot.database.schema.hero.hero_instance import (
    HeroInstance, HeroInstanceData, HeroList)
from albedo_bot.cogs.checklist.utils.checklist_comparison import (
    ChecklistComparison)


class BaseChecklistCog(BaseCog):
    """_summary_

    Args:
        BaseCog (_type_): _description_
    """

    async def _add_checklist(self, ctx: commands.Context, checklist_name: str,
                             description: str):
        """
        Create/add a new checklist to the database under the name\
            `checklist_name`

        Args:
            checklist_name (str): _description_
            description (str): _description_
        """
        checklist_object = self.db_select(Checklist).where(
            Checklist.name == checklist_name)

        checklist_object = await self.db_execute(checklist_object).first()

        if checklist_object is None:

            new_checklist = Checklist(
                name=checklist_name, description=description)
            await self.db_add(new_checklist)

            await send_embed(ctx, embed_wrapper=EmbedWrapper(
                title="Checklist Created",
                description=(
                    f"Successfully created Checklist `{checklist_name}`")))
        else:
            raise CogCommandError(embed_wrapper=EmbedWrapper(
                title="Duplicate Checklist Name",
                description=(
                    f"Checklist with name `{checklist_name}` already exists")))

    async def _list_checklist(self):
        """_summary_

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        """

        checklist_select = self.db_select(Checklist)
        checklist_objects = await self.db_execute(checklist_select).all()

        return checklist_objects

    async def _add_hero(self, ctx: commands.Context, checklist: Checklist,
                        hero: Hero,
                        ascension: AscensionValue,
                        signature_item: SignatureItemValue,
                        furniture: FurnitureValue,
                        engraving: EngravingValue):
        """_summary_

        Args:
            checklist_name (str): _description_
            hero_name (str): _description_
        """

        checklist_hero_select = self.db_select(
            ChecklistHero).where(ChecklistHero.hero_id == hero.id)

        checklist_hero_object = await self.db_execute(
            checklist_hero_select).first()

        si_value = signature_item.si_value
        ascension_value = ascension.ascension_value
        furniture_value = furniture.furniture_value
        engraving_value = engraving.engraving_value

        if checklist_hero_object is None:
            checklist_hero_object = ChecklistHero(
                checklist_name=checklist.name, hero_id=hero.id,
                signature_level=si_value, furniture_level=furniture_value,
                ascension_level=ascension_value,
                engraving_level=engraving_value)

            heroes_string = await self.fetch_heroes(checklist_hero_object)
            await send_embed(ctx, embed_wrapper=EmbedWrapper(
                title="Checklist Hero Added",
                description=(
                    f"Successfully added `{hero.name}` to `{checklist.name}`\n"
                    f"{heroes_string}")))
        else:
            checklist_hero_object.ascension_level = ascension_value
            checklist_hero_object.signature_level = si_value
            checklist_hero_object.furniture_level = furniture_value
            checklist_hero_object.engraving_level = engraving_value

            heroes_string = await self.fetch_heroes(checklist_hero_object)
            await send_embed(ctx, embed_wrapper=EmbedWrapper(
                title="Checklist Hero Created",
                description=(
                    f"Successfully updated `{hero.name}` in "
                    f"`{checklist.name}`\n{heroes_string}")))
        await self.db_add(checklist_hero_object)

    async def _show_checklist(self, checklist: Checklist):
        """
        Get all heroes currently in `checklist`

        Args:
            checklist (Checklist): _description_
        """

        checklist_heroes_select = self.db_select(ChecklistHero).where(
            ChecklistHero.checklist_name == checklist.name)
        return await self.db_execute(checklist_heroes_select).all()

    async def fetch_heroes(self, checklist_hero: list[ChecklistHero]):
        """_summary_

        Args:
            hero_list (List[HeroInstance]): _description_
        """
        hero_instance_tuples = await HeroInstanceData.from_checklist_hero(
            self, checklist_hero)

        heroes_message_object = HeroList(self.bot, hero_instance_tuples)
        output = await heroes_message_object.async_str()
        return output

    async def _remove_checklist(self, ctx: commands.Context,
                                checklist: Checklist):
        """_summary_

        Args:
            checklist_name (str): _description_
        """

        checklist_name = checklist.name

        await self.db_delete(checklist)
        await send_embed(ctx, embed_wrapper=EmbedWrapper(
            title="Checklist removed",
            description=(f"Successfully removed checklist `{checklist_name}`")))

    async def _remove_hero(self, ctx: commands.Context, checklist: Checklist,
                           hero: Hero):
        """_summary_

        Args:
            ctx (_type_): _description_
            checklist (Checklist): _description_
            hero (Hero): _description_
        """

        select_checklist_hero = self.db_select(ChecklistHero).where(
            ChecklistHero.hero_id == hero.id,
            ChecklistHero.checklist_name == checklist.name)

        checklist_hero_object = await self.db_execute(
            select_checklist_hero).first()

        if checklist_hero_object is None:
            embed_wrapper = EmbedWrapper(
                title="Missing hero",
                description=(f"The following hero `{hero.name}` could not be "
                             f"found in checklist `{checklist.name}`"))
            raise CogCommandError(embed_wrapper=embed_wrapper)
        else:
            hero_instance_tuples = await HeroInstanceData.from_checklist_hero(
                self, checklist_hero_object)
            removed_heroes = await self.fetch_heroes(hero_instance_tuples)
            await self.db_delete(checklist_hero_object)

            await send_embed(ctx, embed_wrapper=EmbedWrapper(
                title="Removed Hero",
                description=(f"The following heroes have been successfully "
                             f"removed from checklist `{checklist.name}`\n"
                             f"{removed_heroes}")))

    async def _check_roster(self, ctx: commands.Context, checklist: Checklist,
                            roster_user: User):
        """_summary_

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            checklist (Checklist): _description_
        """
        checklist_heroes_select = self.db_select(ChecklistHero).where(
            ChecklistHero.checklist_name == checklist.name)
        checklist_heroes = await self.db_execute(
            checklist_heroes_select).all()

        roster_heroes_select = self.db_select(HeroInstance).where(
            HeroInstance.player_id == roster_user.id)

        roster_heroes: list[HeroInstance] = await self.db_execute(
            roster_heroes_select).all()

        checklist_compare = ChecklistComparison(self.bot,
                                                checklist_heroes,
                                                roster_heroes)

        heroes_str = await checklist_compare.format_heroes()

        await send_embed(ctx, embed_wrapper=EmbedWrapper(
            title=f"Missing Heroes for checklist \"{checklist.name}\"",
            description=(
                f"{roster_user.mention} is missing the following heroes\n"
                f"{heroes_str}")))
