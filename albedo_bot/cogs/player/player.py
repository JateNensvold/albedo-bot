from typing import TYPE_CHECKING

import discord
from discord.ext import commands
from discord import Role, Member

from albedo_bot.database.schema.guild import Guild
from albedo_bot.database.schema.player import Player
from albedo_bot.utils.errors import CogCommandError
from albedo_bot.cogs.player.utils.base_player import BasePlayerCog
from albedo_bot.utils.message import EmbedWrapper, send_embed


if TYPE_CHECKING:
    from albedo_bot.bot import AlbedoBot


class PlayerCog(BasePlayerCog):
    """
    A group of commands for managing players in an AFK guild


    Args:
        commands (_type_): _description_
    """

    @commands.command(name="register", cog=False)
    async def register(self, ctx: commands.Context, guild: Role = None):
        """
        Register yourself with the bot and assign yourself a guild! The guild 
        can be specified or left blank to allow for automatic detection

        Args:
            ctx (commands.Context): invocation context containing information on
                how a discord event/command was invoked
            guild (Role, optional): A discord Role, Role ID or Role Mention.
                Defaults to None.

        Raises:
            CogCommandError: Player is already registered
            CogCommandError: Auto detection failed because player does not
                have a guild associated with them on discord
            CogCommandError: Auto detection failed because player is in too
                many discord guilds
        """

        member_object: Member = ctx.author

        player_select = self.db_select(Player).where(
            Player.discord_id == member_object.id)
        output = await self.db_execute(player_select).first()
        if output is not None:
            roles = ctx.author.roles
            guild_select = self.db_select(Guild).where(
                Guild.discord_id.in_([role.id for role in roles]))

            guild_result = await self.db_execute(guild_select).first()

            embed_wrapper = EmbedWrapper(
                title="Player Already Registered",
                description=(
                    f"{member_object.mention} is already registered with "
                    f"guild {guild_result}"))
            raise CogCommandError(embed_wrapper=embed_wrapper)
        if guild:
            guild_role = guild
        else:
            roles = ctx.author.roles
            guild_select = self.db_select(Guild).where(
                Guild.discord_id.in_([role.id for role in roles]))

            guild_result = await self.db_execute(guild_select).all()

            if len(guild_result) == 0:
                embed_wrapper = EmbedWrapper(
                    title="Player Error",
                    description=(
                        f"{member_object.mention} needs to be in a guild "
                        "before they can register"))
                raise CogCommandError(embed_wrapper=embed_wrapper)
            elif len(guild_result) > 1:
                member_guilds = ','.join(
                    [f'{guild_object}' for guild_object in guild_result])
                embed_wrapper = EmbedWrapper(
                    title="Player Error",
                    description=(
                        "Cannot detect guild for user "
                        f"{member_object.mention}. To allow for automatic "
                        "guild detection player must have only one of the "
                        f"following roles ({member_guilds}) or should specify "
                        "the <@guild-id> they are registering with"))
                raise CogCommandError(embed_wrapper=embed_wrapper)

            guild_role = discord.utils.get(
                ctx.guild.roles, id=guild_result[0].discord_id)

        await self.register_player(ctx, ctx.author, guild_role)

    # pylint: disable=no-member
    @BasePlayerCog.player_admin.command(name="list")
    async def list(self, ctx: commands.Context, name_filter: str = None):
        """
        List all players registered with the bot, optionally filter players by
            providing a `name_filter`

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            name_filter (str): filter to add to player list. Defaults to
                showing all players
        """

        player_list = await self.list_players(name_filter)

        player_strings: list[str] = []

        for player in player_list:
            guild_select = self.db_select(Guild).where(
                Guild.discord_id == player.guild_id)
            guild_result = await self.db_execute(guild_select).first()

            player_strings.append(
                f"{player.mention()} - player=`{repr(player)}`- "
                f"last_update={player.access_time} - guild={guild_result}")

        if len(player_strings):
            players_str = "\n".join(player_strings)
        else:
            players_str = "No players found"

        await send_embed(ctx, embed_wrapper=EmbedWrapper(
            title="Player List", description=players_str))

    # pylint: disable=no-member
    @BasePlayerCog.player_admin.command(name="add", aliases=["register"])
    async def add_for(self, ctx: commands.Context,  guild_member: Member, guild_role: Role):
        """
        Register a `guild_player` with the bot under the guild associated
            with `guild_role`
        Args:
            ctx (commands.Context): invocation context containing information on how
                a discord event/command was invoked
            guild_member (Member): discord users name, user mention, or user ID
            guild_role (Role): A discord Role, Role ID or Role Mention.
        """
        await self.register_player(ctx, guild_member, guild_role)

    # pylint: disable=no-member
    @BasePlayerCog.player_admin.command(name="remove", aliases=["delete"])
    async def delete(self, ctx: commands.Context, guild_member: Member):
        """
        Remove an already registered player from a discord guild

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            guild_member (Member): discord users name, user mention, or user ID
        """
        await self.delete_player(ctx, guild_member)


def setup(bot: "AlbedoBot"):
    """_summary_

    Args:
        bot (AlbedoBot): _description_
    """
    bot.add_cog(PlayerCog(bot, False))
