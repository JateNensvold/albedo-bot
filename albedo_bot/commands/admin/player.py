from discord.ext.commands.context import Context
from discord import Member

from albedo_bot.commands.helpers.player import player
from albedo_bot.commands.helpers.permissions import has_permission
from albedo_bot.commands.helpers.converter import MemberConverter
from albedo_bot.schema import Player, Guild
import albedo_bot.global_values as GV


@player.command(name="delete", aliases=["remove"])
@has_permission("manager")
async def delete(ctx: Context, guild_member: MemberConverter):
    """[summary]

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
    """
    await delete_player(ctx, guild_member)


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
