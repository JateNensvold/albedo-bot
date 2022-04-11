from discord.ext.commands.context import Context
from discord import Member, Role

from albedo_bot.global_values import bot
import albedo_bot.global_values as GV
from albedo_bot.schema import Guild, Player


@bot.group()
async def player(ctx: Context):
    """[summary]

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
    """
    if ctx.invoked_subcommand is None:
        await ctx.send('Invalid sub command passed...')


async def register_player(ctx: Context, discord_member: Member,
                          guild_role: Role):
    """[summary]

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
    """

    guild_result = GV.session.query(Guild).filter_by(
        discord_id=guild_role.id).first()

    if guild_result is None:
        await ctx.send(
            f"'{guild_role.name}' is not a registered guild, ensure it is a "
            "registered guild before adding a player to it")
        return

    player_result = GV.session.query(Player).filter_by(
        discord_id=discord_member.id).first()

    if player_result is not None:
        guild_object = GV.session.query(Guild).filter_by(
            discord_id=player_result.guild_id).first()
        if guild_object is None:
            await ctx.send(
                f"'{discord_member.name}' is registered with guild that no "
                f"longer exists '{player_result.guild_id}'")
        else:
            await ctx.send(
                f"'{discord_member.name}' is already registered with guild "
                f"'{guild_object.name}'")
        return

    new_player = Player(discord_id=discord_member.id,
                        name=discord_member.name, guild_id=guild_role.id)
    GV.session.add(new_player)
    await ctx.send(
        f"'{discord_member.name}' registered with '{guild_result.name}'")


async def delete_player(ctx: Context, author: Member):
    """[summary]

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
        player_id (int): [description]
    """
    player_object = GV.session.query(Player).filter_by(
        discord_id=author.id).first()
    if player_object is None:
        await ctx.send(f"Player '{author.name}' was not registered")
        return
    GV.session.delete(player_object)
    guild_object = GV.session.query(Guild).filter_by(
        discord_id=player_object.guild_id).first()
    await ctx.send(f"Player '{author.name}' was removed from guild "
                   f"{guild_object}")
