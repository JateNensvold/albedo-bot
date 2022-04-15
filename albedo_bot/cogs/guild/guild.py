
from typing import TYPE_CHECKING
from albedo_bot.cogs.utils.message import send_message

from discord.ext import commands
from discord import Role

from albedo_bot.database.schema import Guild
from albedo_bot.cogs.guild.utils.base_guild import BaseGuildCog

from sqlalchemy import select


if TYPE_CHECKING:
    from albedo_bot.bot import AlbedoBot


class GuildCog(BaseGuildCog):
    """_summary_
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

    @guild.command(name="add")
    async def _add(self, ctx: commands.Context, guild_role: Role):
        """[summary]

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            guild_id (Role): [description]
        """
        guild_select = select(Guild).where(Guild.discord_id == guild_role.id)

        select_result = await self.bot.session.execute(guild_select)
        guild_result = select_result.scalars().first()
        if not guild_result:
            new_guild = Guild(discord_id=guild_role.id, name=guild_role.name)

            self.bot.session.add(new_guild)
            await ctx.send(f"Successfully added {new_guild}")
        else:
            await ctx.send(f"{guild_result} is already registered")

    @guild.command(name="remove", alias=["delete"])
    async def remove(self, ctx: commands.Context, guild_role: Role):
        """[summary]

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            guild_id (Role): [description]
        """

        guild_select = select(Guild).where(Guild.discord_id == guild_role.id)

        select_result = await self.bot.session.execute(guild_select)
        guild_result = select_result.scalars().first()
        if guild_result is None:
            await ctx.send(f"{guild_role} has not been registered as a guild")
            return
        await self.bot.session.delete(guild_result)
        await ctx.send(f"Successfully removed {guild_result}")

    @guild.command(name="list")
    async def _list(self, ctx: commands.Context):
        """[summary]

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        """

        guilds_select = self.select(Guild)
        guilds_result = await self.execute(guilds_select).all()
        guilds_str = "\n".join([str(guild) for guild in guilds_result])

        await send_message(ctx, guilds_str)


def setup(bot: "AlbedoBot"):
    """_summary_

    Args:
        bot (AlbedoBot): _description_
    """
    bot.add_cog(GuildCog(bot))
