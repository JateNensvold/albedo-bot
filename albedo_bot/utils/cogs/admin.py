
from discord.ext import commands
from albedo_bot.commands.utils.checks import check_config_permission

class Admin(commands.Cog):
    """_summary_

    Args:
        commands (_type_): _description_
    """


    

    @commands.group(name="admin")
    @check_config_permission("admin")
    async def admin(self, ctx: commands.Context):
        """_summary_

        Args:
            ctx (commands.Context): _description_
        """
        self.bot.get_cog(self)
        if ctx.invoked_subcommand is None:
            ctx.message
            await ctx.send('Invalid sub command passed...')



from discord.ext.commands.context import Context

from albedo_bot.global_values import bot


@has_permission("guild_manager")
async def admin(ctx: Context):
    """
    Group of commands for all tasks that require some higher level of permissions.
    All commands require either' guild manager', 'manager' or 'admin' and higher to run

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
    """
    if ctx.invoked_subcommand is None:
        await ctx.send('Invalid sub command passed...')
