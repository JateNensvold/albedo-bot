from typing import TYPE_CHECKING
from albedo_bot.utils.errors import CogCommandError

import discord
from discord.ext import commands
from discord import Role, Member

from albedo_bot.database.schema.guild import Guild
from albedo_bot.cogs.player.utils.base_player import BasePlayerCog
from albedo_bot.utils.message import EmbedField, send_embed
from albedo_bot.utils.checks import check_config_permission

# from albedo_bot.utils.checks import check_config_permission


if TYPE_CHECKING:
    from albedo_bot.bot import AlbedoBot


class PlayerCog(BasePlayerCog):
    """_summary_

    Args:
        commands (_type_): _description_
    """

    @commands.group(name="player")
    async def player(self, ctx: commands.Context):
        """[summary]

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        """
        # if ctx.invoked_subcommand is None:
        #     await ctx.send('Invalid sub command passed...')

    @player.command(name="register", aliases=["add"])
    async def register(self, ctx: commands.Context, guild: Role = None):
        """[summary]

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        """

        member_object: Member = ctx.author

        if guild:
            guild_role = guild
        else:
            roles = ctx.author.roles
            guild_select = self.select(Guild).where(
                Guild.discord_id.in_([role.id for role in roles]))

            guild_result = await self.execute(guild_select).all()

            if len(guild_result) == 0:
                embed_field = EmbedField(
                    "Player Error",
                    (f"{member_object.mention} needs to be in a guild before "
                     "they can register"))
                raise CogCommandError(embed_field_list=[embed_field])
            elif len(guild_result) > 1:
                member_guilds = ','.join(
                    [f'{guild_object}' for guild_object in guild_result])
                embed_field = EmbedField(
                    "Player Error",
                    (f"Cannot detect guild for user {member_object.mention}. "
                     "To allow for automatic guild detection player must have "
                     f"only one of the following roles ({member_guilds}) "
                     "or should specify the <@guild-id> they are registering "
                     "with"))
                raise CogCommandError(embed_field_list=[embed_field])

            guild_role = discord.utils.get(
                ctx.guild.roles, id=guild_result[0].discord_id)

        await self.register_player(ctx, ctx.author, guild_role)

    @player.command(name="delete", aliases=["remove"])
    @check_config_permission("manager")
    async def delete(self, ctx: commands.Context, guild_member: Member):
        """[summary]

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        """
        await self.delete_player(ctx, guild_member)

    @player.command(name="list")
    @check_config_permission("guild_manager")
    async def list(self, ctx: commands.Context):
        """[summary]

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        """

        player_list = await self.list_players()
        players_str = "\n".join(
            [f"{player.mention()} - `{repr(player)}`"
                for player in player_list])

        if players_str == "":
            players_str = "No players found"

        embed_field = EmbedField(
            name="Player List",
            value=players_str)
        await send_embed(ctx, embed_field_list=[embed_field])

    # @player_command.command(name="add", aliases=["register"])
    # @check_config_permission("manager")
    # async def add(self, ctx: commands.Context,  guild_member: MemberConverter, guild_role: Role):
    #     """[summary]

    #     Args:
    #         ctx (Context): invocation context containing information on how
    #             a discord event/command was invoked
    #     """
    #     await register_player(ctx, guild_member, guild_role)


def setup(bot: "AlbedoBot"):
    """_summary_

    Args:
        bot (AlbedoBot): _description_
    """
    bot.add_cog(PlayerCog(bot, False))
