from typing import TYPE_CHECKING

from discord.ext import commands

from albedo_bot.cogs.utils.mixins.database_mixin import DatabaseMixin

if TYPE_CHECKING:
    from albedo_bot.bot import AlbedoBot


class BaseCog(commands.Cog, DatabaseMixin):
    """_summary_

    Args:
        commands (_type_): _description_
        DatabaseMixin (_type_): _description_
    """

    def __init__(self, bot: "AlbedoBot"):
        self.bot = bot
