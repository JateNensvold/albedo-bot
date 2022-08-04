from typing import TYPE_CHECKING
from albedo_bot.cogs.hero.utils.ascension import AscensionValue
from albedo_bot.cogs.hero.utils.engraving import EngravingValue
from albedo_bot.cogs.hero.utils.furniture import FurnitureValue
from albedo_bot.cogs.hero.utils.signature_item import SignatureItemValue
from albedo_bot.utils.message import EmbedField, EmbedWrapper, send_embed

from discord.ext import commands

from albedo_bot.utils.checks import check_config_permission
from albedo_bot.cogs.checklist.utils.base_checklist import BaseChecklistCog
from albedo_bot.database.schema.hero import Hero
from albedo_bot.database.schema.checklist import Checklist


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
    async def check_roster(self, ctx: commands.Context, checklist: Checklist):
        """
        Check if you have all the required heroes required by `checklist` in
            your roster

        Args:
            ctx (commands.Context): _description_
            checklist (Checklist): checklist getting checked against
        """

        await self._check_roster(ctx, checklist, ctx.author)

    @checklist_command.command(name="list", aliases=[])
    async def list_checklists(self, ctx: commands.Context):
        """
        List all available checklist

        Args:
            ctx (commands.Context): _description_
        """
        checklist_objects = await self._list_checklist()

        embed_wrapper = EmbedWrapper(title="Checklist List")
        for checklist_object in checklist_objects:
            embed_wrapper.add_field(EmbedField(
                name=checklist_object.name,
                value=f"`{checklist_object.description}`"))

        await send_embed(ctx, embed_wrapper=embed_wrapper)

    @checklist_command.command(name="show", aliases=[])
    async def show_checklist(self, ctx: commands.Context, checklist: Checklist):
        """
        Display all the heroes in a `checklist`


        Args:
            ctx (commands.Context): _description_
            checklist (Checklist): checklist being shown
        """
        checklist_heroes = await self._show_checklist(checklist)
        heroes_string = await self.fetch_heroes(checklist_heroes)

        await send_embed(ctx, embed_wrapper=EmbedWrapper(
            title=f"{checklist.name} checklist",
            description=heroes_string))

    @checklist_command.command(name="add", aliases=["update"])
    @check_config_permission("manager")
    async def add_hero(self, ctx: commands.Context, checklist: Checklist, hero: Hero,
                       ascension: AscensionValue,
                       signature_item: SignatureItemValue,
                       furniture: FurnitureValue,
                       engraving: EngravingValue):
        """
        Add a hero to a checklist

        Args:
            ctx (commands.Context): _description_
            checklist (Checklist): Checklist to add to
            hero (Hero): hero name, or id getting added
            ascension (AscensionValue): Ascension level of hero being added
            signature_item (SignatureItemValue): SI Level of hero being added
            furniture (FurnitureValue): Furniture level of hero being added
            engraving (EngravingValue): Engraving level of hero being added
        """
        await self._add_hero(ctx, checklist, hero,
                             ascension, signature_item, furniture, engraving)

    @checklist_command.command(name="remove")
    @check_config_permission("manager")
    async def remove_hero(self, ctx: commands.Context, checklist: Checklist,
                          hero: Hero):
        """
        Remove a hero from `checklist`
        Args:
            ctx (commands.Context): _description_
            checklist (Checklist): checklist to remove from
            hero (Hero): name or id of hero being removed
        """
        await self._remove_hero(ctx, checklist, hero)

    @ checklist_command.command(name="create", aliases=["register"])
    @ check_config_permission("manager")
    async def add_checklist(self, ctx: commands.Context, checklist_name: str,
                            description: str):
        """
        Create a new checklist

        Use " " around the name and description for input that has spaces

        Args:
            ctx (commands.Context): _description_
            checklist_name (str): name of checklist being created
            description (str): Description of checklist
        """
        await self._add_checklist(ctx, checklist_name, description)

    @checklist_command.command(name="delete")
    @check_config_permission("manager")
    async def remove_checklist(self, ctx: commands.Context,
                               checklist: Checklist):
        """
        Delete a checklist

        Args:
            ctx (commands.Context): _description_
            checklist (Checklist): checklist getting deleted
        """
        await self._remove_checklist(ctx, checklist)


def setup(bot: "AlbedoBot"):
    """_summary_

    Args:
        bot (AlbedoBot): _description_
    """
    bot.add_cog(ChecklistCog(bot))
