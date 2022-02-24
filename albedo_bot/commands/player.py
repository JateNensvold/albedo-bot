from discord.ext.commands.context import Context
from discord.utils import get
import albedo_bot.global_values as GV
from albedo_bot.schema import Player, Guild
from albedo_bot.commands.helpers.player import player, register_player


# @bot.group()
# async def player(ctx: Context):
#     """[summary]

#     Args:
#         ctx (Context): invocation context containing information on how
#             a discord event/command was invoked
#     """
#     if ctx.invoked_subcommand is None:
#         await ctx.send('Invalid sub command passed...')


@player.command(name="register", aliases=["add"])
async def register(ctx: Context):
    """[summary]

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
    """

    author_name = ctx.author.name

    roles = ctx.author.roles
    guild_result = GV.session.query(Guild).filter(
        Guild.discord_id.in_([role.id for role in roles])).all()
    print(guild_result)
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

    print(guild_result)
    guild_role = get(ctx.guild.roles, id=guild_result[0].discord_id)
    print(guild_role, type(guild_role))

    await register_player(ctx, ctx.author, guild_role)
