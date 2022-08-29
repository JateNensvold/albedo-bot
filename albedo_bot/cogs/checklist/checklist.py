from typing import TYPE_CHECKING

from discord.ext import commands

from albedo_bot.utils.checks import check_config_permission
from albedo_bot.cogs.checklist.utils.base_checklist import BaseChecklistCog
from albedo_bot.cogs.hero.utils.converter.ascension import AscensionValue
from albedo_bot.cogs.hero.utils.converter.engraving import EngravingValue
from albedo_bot.cogs.hero.utils.converter.furniture import FurnitureValue
from albedo_bot.cogs.hero.utils.converter.signature_item import (
    SignatureItemValue)
from albedo_bot.utils.message.message_send import send_embed
from albedo_bot.utils.embeds import EmbedField, EmbedWrapper
from albedo_bot.cogs.checklist.utils.converter.checklist import ChecklistValue
from albedo_bot.cogs.hero.utils.converter.hero import HeroValue


if TYPE_CHECKING:
    from albedo_bot.bot import AlbedoBot


class ChecklistCog(BaseChecklistCog):
    """_summary_

    Args:
        BaseChecklistCog (_type_): _description_
    """

    @commands.group(name="checklist")
    async def checklist_command(self, ctx: commands.Context):
        """
        A group of commands used to interact with Checklists. A checklist is a
        group of heroes that have been pinned to certain investment levels to
        show the minimum required investment for the corresponding group

        Ex. A checklist called "AE Heroes" could have the following in it
        showing that these AE Heroes need to be at least at this investment
        level

        `Ainz SI 30 FI 9 E60`
        `Albedo SI 30 FI 3 E0`

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        """

    @checklist_command.command(name="check")
    async def check_roster(self, ctx: commands.Context,
                           checklist: ChecklistValue):
        """
        Check if you have all the required heroes required by `checklist` in
            your roster

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            checklist (Checklist): checklist getting checked against
        """

        await self._check_roster(ctx, checklist.checklist, ctx.author)

    @checklist_command.command(name="list", aliases=[])
    async def list_checklists(self, ctx: commands.Context):
        """
        List all available checklist

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        """
        checklist_objects = await self._list_checklist()

        embed_wrapper = EmbedWrapper(title="Checklist List")
        for checklist_object in checklist_objects:
            embed_wrapper.add_field(EmbedField(
                name=checklist_object.name,
                value=f"`{checklist_object.description}`"))

        await send_embed(ctx, embed_wrapper=embed_wrapper)

    @checklist_command.command(name="show", aliases=[])
    async def show_checklist(self, ctx: commands.Context,
                             checklist: ChecklistValue):
        """
        Display all the heroes in a `checklist`


        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            checklist (Checklist): checklist being shown
        """
        checklist_heroes = await self._show_checklist(checklist.checklist)
        heroes_string = await self.fetch_heroes(checklist_heroes)

        await send_embed(ctx, embed_wrapper=EmbedWrapper(
            title=f"{checklist.checklist.name} checklist",
            description=heroes_string))

    @checklist_command.command(name="add", aliases=["update"])
    @check_config_permission("manager")
    async def add_hero(self, ctx: commands.Context, checklist: ChecklistValue,
                       hero: HeroValue,
                       ascension: AscensionValue,
                       signature_item: SignatureItemValue,
                       furniture: FurnitureValue,
                       engraving: EngravingValue):
        """
        Add a hero to a checklist

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            checklist (Checklist): Checklist to add to
            hero (HeroValue): hero name, or id getting added
            ascension (AscensionValue): Ascension level of hero being added
            signature_item (SignatureItemValue): SI Level of hero being added
            furniture (FurnitureValue): Furniture level of hero being added
            engraving (EngravingValue): Engraving level of hero being added
        """
        await self._add_hero(ctx, checklist.checklist, hero.hero,
                             ascension, signature_item, furniture, engraving)

    @checklist_command.command(name="remove")
    @check_config_permission("manager")
    async def remove_hero(self, ctx: commands.Context,
                          checklist: ChecklistValue,
                          hero: HeroValue):
        """
        Remove a hero from `checklist`
        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            checklist (Checklist): checklist to remove from
            hero (Hero): name or id of hero being removed
        """
        await self._remove_hero(ctx, checklist.checklist, hero.hero)

    @ checklist_command.command(name="create", aliases=["register"])
    @ check_config_permission("manager")
    async def add_checklist(self, ctx: commands.Context, checklist_name: str,
                            description: str):
        """
        Create a new checklist

        Use " " around the name and description for input that has spaces

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            checklist_name (str): name of checklist being created
            description (str): Description of checklist
        """
        await self._add_checklist(ctx, checklist_name, description)

    @checklist_command.command(name="delete")
    @check_config_permission("manager")
    async def remove_checklist(self, ctx: commands.Context,
                               checklist: ChecklistValue):
        """
        Delete a checklist

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            checklist (Checklist): checklist getting deleted
        """
        await self._remove_checklist(ctx, checklist.checklist)


async def setup(bot: "AlbedoBot"):
    """_summary_

    Args:
        bot (AlbedoBot): _description_
    """
    await bot.add_cog(ChecklistCog(bot))
