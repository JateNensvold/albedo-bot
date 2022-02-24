from albedo_bot.commands.helpers.permissions import has_permission
from discord.ext.commands.context import Context

import albedo_bot.global_values as GV
from albedo_bot.schema import Guild
from albedo_bot.commands.helpers.converter import GuildConverter
from albedo_bot.commands.helpers.guild import guild


@guild.command(name="add")
@has_permission("manager")
async def _add(ctx: Context, guild_id: GuildConverter):
    """[summary]

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
        guild_id (Role): [description]
    """
    new_guild = Guild(discord_id=guild_id.id, name=guild_id.name)
    GV.session.add(new_guild)
    await ctx.send(f"Successfully added {new_guild}")


@guild.command(name="remove", alias=["delete"])
@has_permission("manager")
async def remove(ctx: Context, guild_role: GuildConverter):
    """[summary]

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
        guild_id (Role): [description]
    """

    guild_object = GV.session.query(Guild).filter_by(
        discord_id=guild_role.id).first()
    if guild_object is None:
        await ctx.send(f"{guild_role} has not been registered as a guild")
        return
    GV.session.delete(guild_object)
    await ctx.send(f"Successfully removed {guild_object}")


@guild.command(name="list")
@has_permission("guild_manager")
async def _list(ctx: Context):
    """[summary]

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
    """
    guilds = GV.session.query(Guild)
    await ctx.send("\n".join([f"`{guild_object}`" for guild_object in guilds]))
