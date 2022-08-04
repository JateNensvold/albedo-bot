
from typing import TYPE_CHECKING

from discord.ext import commands
from discord import Role

from albedo_bot.database.schema import Guild
from albedo_bot.cogs.guild.utils.base_guild import BaseGuildCog
from albedo_bot.utils.message import EmbedWrapper, send_embed
from albedo_bot.utils.errors import CogCommandError

if TYPE_CHECKING:
    from albedo_bot.bot import AlbedoBot


class GuildCog(BaseGuildCog):
    """_summary_

    Args:
        BaseGuildCog (_type_): _description_

    Raises:
        CogCommandError: _description_
        CogCommandError: _description_
    """
    _summary_ = "A collections of commands for managing afk arena guilds"

    # pylint: disable=no-member
    @BaseGuildCog.guild_admin.command(name="add", aliases=["register"])
    async def _add(self, ctx: commands.Context, guild_role: Role):
        """
        Add/register a new guild

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            guild_role (Role): a discord role, role mention, or role ID
        """

        guild_select = self.db_select(Guild).where(
            Guild.discord_id == guild_role.id)

        guild_object = await self.db_execute(guild_select).first()

        if not guild_object:
            new_guild = Guild(discord_id=guild_role.id, name=guild_role.name)

            self.bot.session.add(new_guild)
            await send_embed(ctx, embed_wrapper=EmbedWrapper(
                description=f"Successfully added guild {new_guild}"))
        else:
            embed_wrapper = EmbedWrapper(
                title="Guild Error",
                description=f"{guild_object} is already a registered guild")
            raise CogCommandError(embed_wrapper=embed_wrapper)

    # pylint: disable=no-member
    @BaseGuildCog.guild_admin.command(name="delete", aliases=["remove"])
    async def delete(self, ctx: commands.Context, guild_role: Role):
        """
        Delete/Remove an existing guild registered with the bot

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            guild_role (Role): a discord role, role mention, or role ID
        """

        guild_select = self.db_select(Guild).where(
            Guild.discord_id == guild_role.id)

        guild_object = await self.db_execute(guild_select).first()
        if guild_object is None:
            embed_wrapper = EmbedWrapper(
                title="Guild Error",
                description=(
                    f"{guild_role.mention} has not been registered as a guild"))
            raise CogCommandError(embed_wrapper=embed_wrapper)

        await self.db_delete(guild_object)
        await send_embed(ctx, embed_wrapper=EmbedWrapper(
            description=f"Successfully removed guild {guild_object}"))

    # pylint: disable=no-member
    @BaseGuildCog.guild_admin.command(name="list")
    async def _list(self, ctx: commands.Context):
        """
        List all guilds registered with the bot

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        """

        guilds_select = self.db_select(Guild)
        guilds_result = await self.db_execute(guilds_select).all()
        guilds_str = "\n".join(
            [f"{guild} - `{repr(guild)}`" for guild in guilds_result])

        if guilds_str == "":
            guilds_str = "No guilds found"

        await send_embed(ctx, embed_wrapper=EmbedWrapper(
            title="Guild List", description=guilds_str))


def setup(bot: "AlbedoBot"):
    """_summary_

    Args:
        bot (AlbedoBot): _description_
    """
    bot.add_cog(GuildCog(bot, False))
