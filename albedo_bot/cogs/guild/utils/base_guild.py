
from discord.ext import commands

from albedo_bot.cogs.utils.base_cog import BaseCog


class BaseGuildCog(BaseCog):
    """_summary_
    """

    @BaseCog.admin.group(name="guild")
    async def guild_admin(self, ctx: commands.Context):
        """
        A group of guild commands that require elevated permissions to run

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        """
