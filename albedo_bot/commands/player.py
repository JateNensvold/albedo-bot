from discord.ext.commands.context import Context
from discord import Member

from albedo_bot.commands.base import bot, session
from albedo_bot.schema import Player, Guild


@bot.group()
async def player(ctx: Context):
    """[summary]

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
    """
    if ctx.invoked_subcommand is None:
        await ctx.send('Invalid sub command passed...')


@player.command(name="register", aliases=["add"])
async def register(ctx: Context):
    """[summary]

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
    """

    author_id = ctx.author.id
    author_name = ctx.author.name

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

    # if guild_id is not None:
    #     guild_result = session.query(Guild).filter_by(
    #         discord_id=guild_id).all()
    # else:
    roles = ctx.author.roles
    guild_result = session.query(Guild)
    guild_result = guild_result.filter(
        Guild.discord_id.in_([role.id for role in roles])).all()

    register_player(ctx)


async def register_player(ctx: Context, player_id: int, guild_id: int):
    """[summary]

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
    """

    guild_result = session.query(Guild).filter_by(discord_id=guild_id).first()

    if guild_result is None:
        await ctx.send(
            f"'{guild_id}' is not a valid <guild-id>, ensure it is a "
            "registered guild before adding a player to it")
        return

    player_result = session.query(Player).filter_by(
        discord_id=player_id).first()
    discord_player_object: Member = ctx.message.server.get_member(player_id)
    author_name = discord_player_object.name

    if player_result is not None:
        guild_object = session.query(Guild).filter_by(
            discord_id=player_result[0].guild_id).all()

        await ctx.send(
            f"'{discord_player_object.name}' is already registered with guild "
            f"'{guild_object[0].name}'")
        return

    new_player = Player(discord_id=player_id,
                        name=author_name, guild_id=guild_id)
    session.add(new_player)
    await ctx.send(
        f"'{author_name}' registered with '{guild_result[0].name}'")
