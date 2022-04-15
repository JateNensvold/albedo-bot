from typing import TYPE_CHECKING
from albedo_bot.cogs.utils.message import send_message

import discord
from discord.ext import commands
from discord import Role, Member

from albedo_bot.database.schema.guild import Guild
from albedo_bot.cogs.player.utils.base_player import BasePlayerCog

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

    @player.command(name="register", alias=["add"])
    async def register(self, ctx: commands.Context, guild: Role = None):
        """[summary]

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        """

        author_name = ctx.author.name

        if guild:
            guild_role = guild
        else:
            roles = ctx.author.roles
            guild_select = self.select(Guild).where(
                Guild.discord_id.in_([role.id for role in roles]))

            guild_result = await self.execute(guild_select).all()

            if len(guild_result) == 0:
                await ctx.send(f"'{author_name}' needs to be in a guild before "
                               "they can register")
                return
            elif len(guild_result) > 1:
                await ctx.send(
                    (f"Cannot detect guild for user '{author_name}'. To allow for "
                     "guild detection player must have only one of the following roles "
                     f"'{[guild_object.name for guild_object in guild_result]}' or "
                     "should specify the <guild-id> they are registering with "))
                return

            guild_role = discord.utils.get(
                ctx.guild.roles, id=guild_result[0].discord_id)

        await self.register_player(ctx, ctx.author, guild_role)

    @player.command(name="delete")
    async def delete(self, ctx: commands.Context, guild_member: Member):
        """[summary]

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        """
        await self.delete_player(ctx, guild_member)

    @player.command(name="list")
    async def list(self, ctx: commands.Context):
        """[summary]

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        """

        player_list = await self.list_players()
        players_str = "\n".join([str(player) for player in player_list])

        await send_message(ctx, players_str)

    # @player_command.command(name="add", aliases=["register"])
    # @has_permission("manager")
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
    bot.add_cog(PlayerCog(bot))
