from discord.ext import commands

from albedo_bot.utils.embeds.embed_wrapper import EmbedWrapper


class MessageError(commands.CommandError):
    """
    A base error message for all discord.py relate errors that need
    to be raised
    """

    #pylint: disable=keyword-arg-before-vararg
    def __init__(self, message: str = None, *args,
                 embed_wrapper: EmbedWrapper = None):
        """
        Initialize the exception error `message` and `EmbedWrapper` from 
            `message` or  the `embed_wrapper` passed in

        Args:
            message (str, optional): The description of the error. 
                Defaults to None.
            embed_wrapper (EmbedWrapper, optional): An embed Wrapper 
                around an exception. Defaults to None.
        """
        if message is None:
            message = f"{embed_wrapper.title}\n{embed_wrapper.description}"

        if embed_wrapper is None:
            self.embed_wrapper = EmbedWrapper(title=self.__class__.__name__,
                                              description=message)
        else:
            self.embed_wrapper = embed_wrapper
        super().__init__(message, *args)


class RemoteProcessingError(MessageError):
    """
    Raised when an issue occurs while interacting with a
    remote/external process
    """


class DiscordPermissionError(MessageError, commands.CheckFailure):
    """
    Raised when any discord.py permissions issues occur 
    """


class UnregisteredUserError(MessageError, commands.CheckFailure):
    """
    Raised when an unregistered user attempts attempt to use a command
    """


class CogCommandError(MessageError):
    """
    Raised when an issue occurs in a discord.py cog 
    """


class FileParsingError(MessageError):
    """
    Raised when an issue occurs while parsing an external File
    """


class ConversionError(MessageError):
    """
    Raised when a discord.py Conversion error occurs
    """


class DatabaseError(MessageError):
    """
    A general error for all database related issues
    """


class PreCommitException(DatabaseError):
    """
    Raised when a Pre Commit hook fails while adding an object to the database
    """


class DatabaseSessionError(DatabaseError):
    """
    Raised when any database session errors issues occur
    """
