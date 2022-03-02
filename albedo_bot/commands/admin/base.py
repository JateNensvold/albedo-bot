
from discord.ext.commands.context import Context

from albedo_bot.global_values import bot


@bot.group(name="admin")
async def admin(ctx: Context):
    """[summary]

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
    """
    if ctx.invoked_subcommand is None:
        await ctx.send('Invalid sub command passed...')
