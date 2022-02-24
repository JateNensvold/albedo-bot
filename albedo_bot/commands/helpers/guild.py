
from albedo_bot.global_values import bot
from discord.ext.commands.context import Context


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
