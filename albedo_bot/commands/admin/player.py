@player.command(name="delete", aliases=["remove"])
async def delete(ctx: Context):
    """[summary]

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
    """
    player_id = ctx.author.discord_id
    delete_player(ctx, player_id)


async def delete_player(ctx: Context, player_id: int):
    """[summary]

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
        player_id (int): [description]
    """
    player_objects = session.query(Player).filter_by(
        discord_id=player_id).first()
    if player_objects is None:
        ctx.send("Unable to find a player with ")
    session.delete()
