from discord.ext.commands.context import Context
from discord import Role

from albedo_bot.commands.base import bot, session
from albedo_bot.schema import Guild


@bot.group()
async def guild(ctx: Context):
    """
    Grouping for guild subcommands


    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
    """


    if ctx.invoked_subcommand is None:
        await ctx.send('Invalid sub command passed...')


@guild.command(name="add")
async def _add(ctx: Context, guild_id: Role):
    """[summary]

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
        guild_id (Role): [description]
    """
    new_guild = Guild(discord_id=guild_id.id, name=guild_id.name)
    session.add(new_guild)
    await ctx.send(str(new_guild))


@guild.command(name="list")
async def _list(ctx: Context):
    """[summary]

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
    """
    guilds = session.query(Guild)
    await ctx.send("\n".join([str(guild_object) for guild_object in guilds]))
