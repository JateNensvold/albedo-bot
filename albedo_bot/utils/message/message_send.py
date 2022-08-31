from typing import Union
from albedo_bot.utils.message.message import MessageWrapper

from discord.ext.commands.context import Context
from discord import Embed, Message, File


from albedo_bot.utils.errors import MessageError
from albedo_bot.utils.emoji import red_x, white_check_mark
from albedo_bot.utils.embeds.select import SelectView
from albedo_bot.utils.embeds.embed_utils import generate_embeds
from albedo_bot.utils.embeds.embed_wrapper import EmbedWrapper

#  The following fields were once supported and are will not
#       be supported again until a use case arises
#  header: str = "",
#  css: bool = False,
#  wrapper: str = "",


async def send_message(ctx: Context,
                       text: str,
                       embed_wrapper: EmbedWrapper | list[EmbedWrapper],
                       embed: Embed = None,
                       reply: bool = True,
                       mention_author: bool = False,
                       embed_color: str = "green",
                       emoji: str = white_check_mark,
                       file: File | list[File] = None,
                       view: SelectView = None):

    """
    Send a discord message constructed from text, embed_wrapper, embed, 
    view and Files. This function does the same thing as send_embed but also
    allows users to send text

    Args:
        ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        text (str): text to send in discord message
        embed_wrapper (EmbedWrapper, optional): Embed wrapper to construct an
            embed out of. Defaults to None.
        embed (Embed, optional): Embed to send. Defaults to None.
        reply (bool, optional): reply to the original message in the embed
            message. Defaults to True.
        mention_author (bool, optional): mention discord users in the message
            when True. Defaults to False.
        embed_color (str, optional): Color to set the embed colors to.
            Defaults to "green".
        emoji (str, optional): Emoji to put at the start of the embed Title.
            Defaults to white_check_mark.
        edit_message (Message, optional): When a message is provided it means
            that the embed that would get sent in the message should instead be
            attached to the message provided . Defaults to None.
        file (File | list[File]): File or list of files to
            send in message. Defaults to None.
        view (SelectView, optional): Discord view object to send in
            message(may contain selection or other discord embed types).
            Defaults to None.

    Returns:
        (list[Message]): returns the messages generated to send the
            embeds
    """

    message_wrapper = MessageWrapper(ctx=ctx,
                                     text=text,
                                     embed_wrappers=embed_wrapper,
                                     embeds=embed,
                                     files=file,
                                     view=view,
                                     emoji=emoji,
                                     embed_color=embed_color)

    return await message_wrapper.send(repl=reply,
                                      mention_author=mention_author)


async def send_embed(ctx: Context,
                     embed_wrapper: EmbedWrapper | list[EmbedWrapper],
                     embed: Embed = None,
                     reply: bool = True,
                     mention_author: bool = False,
                     embed_color: str = "green",
                     emoji: str = white_check_mark,
                     file: File | list[File] = None,
                     view: SelectView = None):
    """
    Send an embed Message containing `embed`. If an `embed_wrapper` is provided
    an embed will be constructed from it.

    Args:
        ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        embed_wrapper (EmbedWrapper, optional): Embed wrapper to construct an
            embed out of. Defaults to None.
        embed (Embed, optional): Embed to send. Defaults to None.
        reply (bool, optional): reply to the original message in the embed
            message. Defaults to True.
        mention_author (bool, optional): mention discord users in the message
            when True. Defaults to False.
        embed_color (str, optional): Color to set the embed colors to.
            Defaults to "green".
        emoji (str, optional): Emoji to put at the start of the embed Title.
            Defaults to white_check_mark.
        edit_message (Message, optional): When a message is provided it means
            that the embed that would get sent in the message should instead be
            attached to the message provided . Defaults to None.
        file (File | list[File]): File or list of files to
            send in message. Defaults to None.
        view (SelectView, optional): Discord view object to send in
            message(may contain selection or other discord embed types).
            Defaults to None.

    Returns:
        (list[Message]): returns the messages generated to send the
            embeds
    """

    message_wrapper = MessageWrapper(ctx=ctx,
                                     text=None,
                                     embed_wrappers=embed_wrapper,
                                     embeds=embed,
                                     files=file,
                                     view=view,
                                     emoji=emoji,
                                     embed_color=embed_color)

    return await message_wrapper.send(reply=reply,
                                      mention_author=mention_author)


async def edit_message(ctx: Context,
                       message: Message,
                       content: str = None,
                       embed_wrapper: Union[EmbedWrapper,
                                            list[EmbedWrapper]] = None,
                       embed: Embed = None,
                       embed_color: str = "green",
                       emoji: str = white_check_mark,
                       file: Union[File, list[File]] = None,
                       view: SelectView = None):
    """
    Edit a Message containing an `embed`. If an `embed_wrapper` is provided
    an embed will be constructed from it.

    Args:
        ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        message (Message, optional): Message getting edited
        content(str, optional): text content to put in message
            Defaults to None. 
        embed_wrapper (EmbedWrapper, optional): Embed wrapper to construct an
            embed out of. Defaults to None.
        embed (Embed, optional): Embed to send. Defaults to None.
        embed_color (str, optional): Color to set the embed colors to.
            Defaults to "green".
        emoji (str, optional): Emoji to put at the start of the embed Title.
            Defaults to white_check_mark.
        file (Union[File, list[File]], optional): File or list of files to
            send in message. Defaults to None.
        view (SelectView, optional): Discord view object to send in
            message(may contain selection or other discord embedded types).
            Defaults to None.
    Returns:
        Message: the message sent in discord
    """

    files: list[File] = []
    if isinstance(file, File):
        files = [file]
    elif isinstance(file, list):
        files = file

    embed_list = generate_embeds(ctx, files, embed_wrapper=embed_wrapper,
                                 embed=embed, embed_color=embed_color,
                                 emoji=emoji)

    return await message.edit(content=content, embeds=embed_list, view=view,
                              attachments=files)


async def send_embed_exception(ctx: Context, exception: MessageError,
                               description: str = None, **kwargs):
    """
    Send an exception as an embed message

    Args:
        ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        exception (MessageError): exception to send
        description (str, Optional): a description that will be added to the 
            embed description before the exception text. Defaults to None
    Returns:
        (list[Message]): returns the messages generated to send the
            embeds
    """
    embed_wrapper = None

    if isinstance(exception, MessageError):
        embed_wrapper = exception.embed_wrapper

        if not embed_wrapper.title:
            embed_wrapper.title = exception.__class__.__name__
    else:
        embed_wrapper = EmbedWrapper(title=exception.__class__.__name__,
                                     description=str(exception))
    if description is not None:
        embed_wrapper.description = (
            f"{description}\n{embed_wrapper.description}")
    kwargs["embed_color"] = kwargs.get("embed_color", "red")
    kwargs["emoji"] = kwargs.get("emoji", red_x)

    return await send_embed(ctx, embed_wrapper=embed_wrapper, **kwargs)
