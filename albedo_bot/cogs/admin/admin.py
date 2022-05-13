
from discord.ext import commands
from albedo_bot.utils.checks import check_config_permission


class AdminCog(commands.Cog):
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
        # self.bot.get_cog(self)
        # if ctx.invoked_subcommand is None:
        #     ctx.message
        #     await ctx.send('Invalid sub command passed...')
