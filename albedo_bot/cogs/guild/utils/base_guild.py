from discord.ext import commands

from albedo_bot.cogs.utils.base_cog import BaseCog
from albedo_bot.utils.checks import check_config_permission


class BaseGuildCog(BaseCog):
    """_summary_
    """

    @BaseCog.admin.group(name="guild")
    @check_config_permission("manager")
    async def guild_admin(self, ctx: commands.Context):
        """
        A group of players commands that require elevated permissions to run

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        """
