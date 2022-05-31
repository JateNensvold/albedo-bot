
from typing import TYPE_CHECKING


from discord.ext import commands
from discord import Role

from albedo_bot.database.schema import Guild
from albedo_bot.cogs.guild.utils.base_guild import BaseGuildCog
from albedo_bot.utils.message import EmbedField, send_embed
from albedo_bot.utils.errors import CogCommandError

if TYPE_CHECKING:
    from albedo_bot.bot import AlbedoBot


class GuildCog(BaseGuildCog):
    """
    testing
    """

    @commands.group(name="guild")
    async def guild(self, ctx: commands.Context):
        """[summary]

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        """
        # if ctx.invoked_subcommand is None:
        #     await ctx.send('Invalid sub command passed...')

    @guild.command(name="add", aliases=["register"])
    async def _add(self, ctx: commands.Context, guild_role: Role):
        """[summary]

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            guild_id (Role): [description]
        """

        guild_select = self.db_select(Guild).where(
            Guild.discord_id == guild_role.id)

        guild_object = await self.db_execute(guild_select).first()

        if not guild_object:
            new_guild = Guild(discord_id=guild_role.id, name=guild_role.name)

            self.bot.session.add(new_guild)
            embed_field = EmbedField(
                value=f"Successfully added guild {new_guild}")
            await send_embed(ctx, embed_field_list=[embed_field])
        else:
            embed_field = EmbedField(
                "Guild Error",
                f"{guild_object} is already a registered guild")
            raise CogCommandError(embed_field_list=[embed_field])

    @guild.command(name="delete", aliases=["remove"])
    async def delete(self, ctx: commands.Context, guild_role: Role):
        """[summary]

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            guild_id (Role): [description]
        """

        guild_select = self.db_select(Guild).where(
            Guild.discord_id == guild_role.id)

        guild_object = await self.db_execute(guild_select).first()
        if guild_object is None:
            embed_field = EmbedField(
                "Guild Error",
                f"{guild_role.mention} has not been registered as a guild")
            raise CogCommandError(embed_field_list=[embed_field])

        await self.db_delete(guild_object)
        embed_field = EmbedField(
            value=f"Successfully removed guild {guild_object}")
        await send_embed(ctx, embed_field_list=[embed_field])

    @guild.command(name="list")
    async def _list(self, ctx: commands.Context):
        """[summary]

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

        embed_field = EmbedField(
            name="Guild List",
            value=guilds_str)
        await send_embed(ctx, embed_field_list=[embed_field])


def setup(bot: "AlbedoBot"):
    """_summary_

    Args:
        bot (AlbedoBot): _description_
    """
    bot.add_cog(GuildCog(bot, False))
