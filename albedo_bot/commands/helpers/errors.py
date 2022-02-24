from discord.ext import commands


class DiscordPermissionError(commands.CheckFailure):
    """_summary_

    Args:
        commands (_type_): _description_
    """


class ErrorHandler(commands.Cog):
    """_summary_

    Args:
        commands (_type_): _description_
    """

    def __init__(self, bot: commands.Bot):
        """_summary_

        Args:
            bot (commands.Bot): _description_
        """
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context,
                               error: Exception):
        """A global error handler cog."""
        message = "".join(error.args)
        print(message)
        await ctx.send(message)
        if isinstance(error, (DiscordPermissionError, commands.BadArgument)):
            return

        raise error
