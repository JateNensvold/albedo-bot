
from typing import TYPE_CHECKING

from discord.ext import commands

if TYPE_CHECKING:
    from albedo_bot.utils.message import EmbedField


class DiscordPermissionError(commands.CheckFailure):
    """_summary_

    Args:
        commands (_type_): _description_
    """


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
    def __init__(self, message=None, *args, embed_field_list: list["EmbedField"] = None):
        """_summary_

        Args:
            message (_type_, optional): _description_. Defaults to None.
            embed (Embed, optional): _description_. Defaults to None.
        """
        self.embed_fields = embed_field_list
        super().__init__(message, *args)


class CogCommandError(MessageError):
    """_summary_

    Args:
        MessageError (_type_): _description_
    """
