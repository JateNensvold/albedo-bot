from typing import TYPE_CHECKING

from discord.ext import commands

if TYPE_CHECKING:
    from albedo_bot.utils.message import EmbedWrapper


class UnregisteredUserError(commands.CheckFailure):
    """_summary_

    Args:
        commands (_type_): _description_
    """


class MessageError(commands.CommandError):
    """_summary_

    Args:
        commands (_type_): _description_
    """

    #pylint: disable=keyword-arg-before-vararg
    def __init__(self, message=None, *args, embed_wrapper: "EmbedWrapper" = None):
        """_summary_

        Args:
            message (_type_, optional): _description_. Defaults to None.
            embed (Embed, optional): _description_. Defaults to None.
        """
        if message is None:
            message = f"{embed_wrapper.title}\n{embed_wrapper.description}"

        self.embed_wrapper = embed_wrapper
        super().__init__(message, *args)


class DiscordPermissionError(MessageError, commands.CheckFailure):
    """_summary_

    Args:
        commands (_type_): _description_
    """


class CogCommandError(MessageError):
    """_summary_

    Args:
        MessageError (_type_): _description_
    """


class ConversionError(MessageError):
    """_summary_

    Args:
        MessageError (_type_): _description_
    """


class DatabaseError(MessageError):
    """_summary_

    Args:
        SQLAlchemyError (_type_): _description_
    """


class DatabaseSessionError(DatabaseError):
    """_summary_

    Args:
        DatabaseError (_type_): _description_
    """
