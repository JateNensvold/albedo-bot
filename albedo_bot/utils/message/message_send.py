from datetime import datetime
from time import time
from typing import Union

from discord.ext.commands.context import Context
from discord import Embed, Message, File

from image_processing.utils.color_helper import MplColorHelper

from albedo_bot.utils.errors import MessageError
from albedo_bot.utils.emoji import red_x, white_check_mark
from albedo_bot.utils.embeds.select import SelectView
from albedo_bot.utils.message.message_util import wrap_message
from albedo_bot.utils.embeds.embed_wrapper import EmbedWrapper


async def send_message(ctx: Context,
                       message: str,
                       header: str = "",
                       css: bool = False,
                       wrapper: str = "",
                       reply: bool = True,
                       mention_author: bool = False,
                       edit_message: Message = None,
                       file: File = None,
                       view: SelectView = None):
    """_summary_

    Args:
        ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        message (str): _description_
        header (str, optional): _description_. Defaults to None.
        css (bool, optional): _description_. Defaults to True.
        wrapper (str, optional): _description_. Defaults to "".
    """
    css_wrapper = "```css\n{}\n```"

    # if header is None or header == "":
    #     header = f"{white_check_mark}\n"

    if css:
        wrapper = css_wrapper
    message_list = wrap_message(message, wrapper=wrapper, header=header)
    await _send_message(ctx, message_list, reply, edit_message, mention_author,
                        view, file)


async def _send_message(ctx: Context,
                        message_list: list[str],
                        reply: bool,
                        edit_message: Message,
                        mention_author: bool,
                        view: SelectView,
                        file: File) -> Message:
    """
    Do the sending/editing of a message and return the response.

    If a message is edited with a text length greater than the message limit
    on discord, the edit will be truncated to the maximum allowed characters

    Args:
        ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        embed (Embed): _description_
        reply (bool): _description_
        edit_message (Message): _description_
        mention_author (bool): _description_

    Returns:
        Message: _description_
    """

    if edit_message is not None:
        return await edit_message.edit(content=message_list[0])

    message_kwargs = {"mention_author": mention_author,
                      "file": file,
                      "view": view}
    for message in message_list:

        if reply:
            return await ctx.reply(message, **message_kwargs)
        else:
            return await ctx.send(message, **message_kwargs)


def generate_embeds(ctx: Context,
                    files: list[File],
                    embed_wrapper: Union[EmbedWrapper,
                                         list[EmbedWrapper]] = None,
                    embed: Embed = None,
                    embed_color: str = "green",
                    emoji: str = white_check_mark):
    """
    Take a list of embed and embed_wrapper and generate all the embeds for a
    message in a list

    Will edit files list in place when embeds contain images

    Args:
        ctx (Context): _description_
        files (list[File]): list of files to send alongside embeds,
            images from embeds get added to this
        embed_wrapper (Union[EmbedWrapper, list[EmbedWrapper]], optional): 
            embed wrapper(s) to turn into embeds. Defaults to None.
        embed (Embed, optional): optional embed that is already created.
            Defaults to None.
        embed_color (str, optional): Color to set embeds while generating them.
            Defaults to "green".
        emoji (str, optional): Emoji to send in embed title.
            Defaults to white_check_mark.

    Returns:
        list[Embed]: list of embeds to send
    """

    embed_list: list[Embed] = []
    if embed:
        embed_list.append(embed)

    color = MplColorHelper().get_unicode(embed_color)
    if isinstance(embed_wrapper, EmbedWrapper):
        _embed_wrappers = [embed_wrapper]
    else:
        _embed_wrappers = embed_wrapper

    embed_wrapper_list: list[EmbedWrapper] = []
    # Initialize any uninitialized content in the embed_wrappers and break
    #   apart the content to fit inside the embed character limits
    for _embed_wrapper in _embed_wrappers:
        if _embed_wrapper.duration is None:
            _embed_wrapper.duration = time() - ctx.start_time
            _embed_wrapper.create_footer()

        if not _embed_wrapper.check_char_limit():
            generated_embed_wrappers = _embed_wrapper.split_embed()
            embed_wrapper_list.extend(generated_embed_wrappers)
        else:
            embed_wrapper_list.append(_embed_wrapper)

    embed_list: list[Embed] = []
    for current_embed_wrapper in embed_wrapper_list:
        current_embed = Embed(
            color=color,
            timestamp=datetime.fromtimestamp(time()))
        if (current_embed_wrapper.title == "" or
                current_embed_wrapper.title is None):
            current_embed.title = f"{emoji} Success"
        elif emoji:
            current_embed.title = f"{emoji} {current_embed_wrapper.title}"
        else:
            current_embed.title = current_embed_wrapper.title
        current_embed.description = current_embed_wrapper.description
        current_embed.set_footer(text=current_embed_wrapper.footer)

        for embed_field in current_embed_wrapper.embed_fields:
            current_embed.add_field(name=embed_field.name,
                                    value=embed_field.value)
        if current_embed_wrapper.image:
            current_embed.set_image(
                url=("attachment://"
                     f"{current_embed_wrapper.image.filename}"))
            files.append(current_embed_wrapper.image)
        embed_list.append(current_embed)
    return embed_list


async def send_embed(ctx: Context,
                     embed_wrapper: Union[EmbedWrapper,
                                          list[EmbedWrapper]],
                     embed: Embed = None,
                     reply: bool = True,
                     mention_author: bool = False,
                     embed_color: str = "green",
                     emoji: str = white_check_mark,
                     file: Union[File, list[File]] = None,
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
        file (Union[File, list[File]], optional): File or list of files to
            send in message. Defaults to None.
        view (SelectView, optional): Discord view object to send in
            message(may contain selection or other discord embed types).
            Defaults to None.

    Returns:
        (list[Message]): returns the messages generated to send the
            embeds
    """

    files: list[File] = []
    if isinstance(file, File):
        files = [file]
    elif isinstance(file, list):
        files = file

    embed_list = generate_embeds(ctx, files, embed_wrapper=embed_wrapper,
                                 embed=embed, embed_color=embed_color,
                                 emoji=emoji)

    for embed in embed_list:
        fields = [embed.title, embed.description, embed.footer.text, embed.author.name]

        fields.extend([field.name for field in embed.fields])
        fields.extend([field.value for field in embed.fields])

        total = ""
        for item in fields:
            # If we str(discord.Embed.Empty) we get 'Embed.Empty', when
            # we just want an empty string...
            total += str(item) if item is not None else ''
        print(embed.title, len(total))

    message_list: list[Message] = []
    while len(embed_list) > 0:
        sent_message = await _send_embed(ctx, embeds=embed_list[:10],
                                         reply=reply,
                                         mention_author=mention_author,
                                         view=view, files=files[:10])
        files = files[10:]
        embed_list = embed_list[10:]
        message_list.append(sent_message)
    return message_list


async def edit_message(ctx: Context,
                       message: Message,
                       content: str = None,
                       embed_wrapper: Union[EmbedWrapper,
                                            list[EmbedWrapper]] = None,
                       embed: Embed = None,
                       mention_author: bool = False,
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
        mention_author (bool, optional): mention discord users in the message
            when True. Defaults to False.
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
                              allowed_mentions=mention_author,
                              attachments=files)


async def _send_embed(ctx: Context,
                      embeds: list[Embed],
                      reply: bool,
                      mention_author: bool,
                      view: SelectView,
                      files: list[File]) -> Message:
    """
    Do the sending/editing of an embed message and return the response

    Args:
        ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        embeds (list[Embed)): Discord Embeds to send in message
        reply (bool): reply to the original message when true
        mention_author (bool): mention discord users in the message
            when True
        file (list[File]): list of files to
                    send in message
    Returns:
        Message: the message sent in discord
    """

    message_kwargs = {"embeds": embeds,
                      "mention_author": mention_author,
                      "view": view,
                      "files": files}
    if reply:
        return await ctx.reply(**message_kwargs)
    else:
        return await ctx.send(**message_kwargs)


async def send_embed_exception(ctx: Context, exception: MessageError, **kwargs):
    """_summary_

    Args:
        ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        exception (MessageError): _description_
    """
    embed_wrapper = None

    if isinstance(exception, MessageError):
        embed_wrapper = exception.embed_wrapper

        # for exception_embed_field in exception_embed_fields:
        #     if exception_embed_field.name is None:
        if not embed_wrapper.title:
            embed_wrapper.title = exception.__class__.__name__
    else:
        embed_wrapper = EmbedWrapper(title=exception.__class__.__name__,
                                     description=str(exception))
    kwargs["embed_color"] = kwargs.get("embed_color", "red")
    kwargs["emoji"] = kwargs.get("emoji", red_x)

    await send_embed(ctx, embed_wrapper=embed_wrapper, **kwargs)
