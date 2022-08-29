
from typing import TYPE_CHECKING
from albedo_bot.cogs.hero.utils.converter.hero import HeroValue

from discord import User
from discord.ext import commands

from albedo_bot.utils.message.message_send import EmbedWrapper, send_embed
from albedo_bot.cogs.roster.utils.base_roster import BaseRosterCog
from albedo_bot.utils.checks import is_registered
from albedo_bot.cogs.hero.utils import (
    AscensionValue, FurnitureValue, SignatureItemValue, EngravingValue)

if TYPE_CHECKING:
    from albedo_bot.bot import AlbedoBot


class RosterCog(BaseRosterCog):
    """
    A group of commands used to manager a players AFK Arena roster
    """

    @commands.group(name="roster")
    @is_registered()
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
            guild_member (User, optional): User name, user mention, or
                user ID to show the roster of . Defaults to showing the roster
                of whoever invoked the command when no user is provided.
        """

        user_id = ctx.author.id
        if guild_member:
            user_id = guild_member.id

        user_object: User = await self.bot.fetch_user(user_id)

        heroes_result = await self.fetch_roster(user_id)
        await send_embed(ctx, embed_wrapper=EmbedWrapper(
            title=f"{user_object.name}'s roster",
            description=heroes_result))

    @roster.command(name="add", aliases=["update"])
    async def _add(self, ctx: commands.Context, hero: HeroValue,
                   ascension: AscensionValue,
                   signature_item: SignatureItemValue,
                   furniture: FurnitureValue,
                   engraving: EngravingValue):
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
        await self.add_hero(ctx, ctx.author, hero.hero, ascension,
                            signature_item, furniture, engraving)
        await self.update_player(ctx.author)

    @roster.command(name="remove", aliases=["delete"])
    async def remove(self, ctx: commands.Context, hero: HeroValue):
        """
        Remove an AFK Arena hero from your roster

        Args:
            ctx (commands.Context): ctx (Context): invocation context
                containing information on how a discord event/command was
                invoked
            hero (Hero): Name or hero ID of hero to remove
        """
        await self.remove_hero(ctx, ctx.author, hero.hero)
        await self.update_player(ctx.author)

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

        await self._upload(ctx)
        await self.update_player(ctx.author)

    @BaseRosterCog.roster_admin.command(name="clear")
    async def clear(self, ctx: commands.Context, discord_user: User):
        """
        Clear a users roster, removing any dependencies preventing them from
            being deleted from the bot

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            discord_user (Member): discord users name, user mention, or user ID
        """

        await self.clear_roster(ctx, discord_user)

    @BaseRosterCog.roster_admin.command(name="dump")
    async def dump(self, ctx: commands.Context):
        """_summary_

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        """
        await self.dump_rosters(ctx)


async def setup(bot: "AlbedoBot"):
    """_summary_

    Args:
        bot (AlbedoBot): _description_
    """
    await bot.add_cog(RosterCog(bot))
