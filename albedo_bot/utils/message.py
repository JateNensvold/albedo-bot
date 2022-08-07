from datetime import datetime
from time import time
from typing import NamedTuple

from discord.ext.commands.context import Context
from discord import Embed, Message, File

from image_processing.utils.color_helper import MplColorHelper

from albedo_bot.utils.errors import MessageError
from albedo_bot.utils.emoji import red_x, white_check_mark, hourglass


class EmbedWrapper:
    """_summary_
    """

    def __init__(self, title: str = None,
                 description: str = "",
                 footer: str = "",
                 embed_fields: list['EmbedField'] = None,
                 duration: float = None,
                 multi_message_compatible: bool = True):
        """_summary_

        Args:
            title (str, optional): Title of embed. Defaults to None.
            description (str, optional): description text of embed.
                Defaults to "".
            footer (str, optional): footer text of embed.
                Default to "".
            embed_fields (list[&#39;EmbedField&#39;], optional):
                List of embed fields.
                Defaults to None.
            duration (float, optional): Length it took to execute command
                Default to None.
            multi_message_compatible (bool, optional): Flag that states the
                embed_wrapper can be broken apart into multiple messages.
                Defaults to True.
        """
        self.title = title
        if embed_fields is None:
            self.embed_fields: list["EmbedField"] = []
        else:
            self.embed_fields = embed_fields
        self.footer = footer
        self.duration = duration
        self.create_footer()

        self.description = description
        self.multi_message_compatible = multi_message_compatible

    def add_field(self, embed_field: "EmbedField"):
        """_summary_

        Args:
            embed_field (EmbedField): _description_
        """
        self.embed_fields.append(embed_field)

    def create_footer(self):
        """
        Adds a duration message to the footer in addition to whatever other
            text it currently has
        """
        if self.duration:
            duration_message = (f"{hourglass} Executed in {self.duration:.2f} "
                                "seconds")
            if self.footer == "":
                self.footer = duration_message
            else:
                self.footer = f"{self.footer}\n{duration_message}"

    def char_limit(self):
        """
        Check if the Embed Wrapper has exceeded

        Returns:
            _type_: _description_
        """
        fields = [self.title, self.description, self.footer]

        fields.extend([field.name for field in self.embed_fields])
        fields.extend([field.value for field in self.embed_fields])

        total = 0
        for item in fields:
            str_item = str(item) if str(item) != 'Embed.Empty' else ''
            total += len(str_item)

        return total

    def check_char_limit(self):
        """_summary_

        Returns:
            _type_: _description_
        """

        if self.char_limit() < 6000 and len(self.description) < 4096:
            return True
        return False

    def split_embed(self):
        """
        Split EmbedWrapper apart into multiple EmbedWrappers that each fit
            under the 6000 character text limit

        Ensures description length is under 4096 char

        *Does not validate length for title, footer or author entries.
        """
        embed_list: list[EmbedWrapper] = []

        latest_embed = None

        if len(self.description) > 4096:
            description_list = wrap_message(
                self.description, max_message_length=4096)
            description_string_index = 0
            while description_string_index < len(description_list):
                description_string = description_list[description_string_index]
                description_string_index += 1
                latest_embed = EmbedWrapper(
                    self.title,
                    description_string,
                    footer=self.footer,
                    multi_message_compatible=self.multi_message_compatible)
                if description_string_index < len(description_list):
                    embed_list.append(latest_embed)
        else:
            latest_embed = EmbedWrapper(
                self.title,
                description_string,
                footer=self.footer,
                multi_message_compatible=self.multi_message_compatible)

        embed_field_index = 0
        while embed_field_index < len(self.embed_fields):
            cur_char_count = latest_embed.check_char_limit()
            cur_embed_field = self.embed_fields[embed_field_index]
            embed_char_count = len(cur_embed_field.name) + \
                len(cur_embed_field.value)
            if cur_char_count + embed_char_count > 6000:
                embed_list.append(latest_embed)
                latest_embed = EmbedWrapper(
                    self.title,
                    footer=self.footer,
                    embed_fields=[cur_embed_field],
                    multi_message_compatible=self.multi_message_compatible)
            embed_field_index += 1

        embed_list.append(latest_embed)

        return embed_list

    def __str__(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        embed_str_list: list[str] = []
        if self.title:
            embed_str_list.append(self.title)
        else:
            embed_str_list.append("No title")

        if self.description:
            embed_str_list.append(self.description)
        else:
            embed_str_list.append("No description")

        if self.footer:
            embed_str_list.append(self.footer)
        else:
            embed_str_list.append("No footer")

        dash_line = '-' * 20
        backslash = "\n"
        return f"{dash_line}\n{backslash.join(embed_str_list)}\n{dash_line}"


class EmbedFooter(NamedTuple):
    """_summary_

    Args:
        NamedTuple (_type_): _description_

    Returns:
        _type_: _description_
    """
    text: str


class EmbedField(NamedTuple("EmbedField", [("name", str),
                                           ("value", str)])):
    """_summary_

    Args:
        NamedTuple (_type_): _description_
    """

    # __init__ method provided as a function stub for type hinting calls to
    #   __new__ construction
    # pylint: disable=super-init-not-called
    def __init__(self, name: str = None, value: str = None):
        """
        Set name and value for `Discord embed_field`

        Args:
            name (str, optional): _description_. Defaults to None.
            value (str, optional): _description_. Defaults to None.
        """

    def __new__(cls: type["EmbedField"],
                name: str = None, value: str = None) -> "EmbedField":
        """_summary_

        Args:
            cls (type[&quot;EmbedField&quot;]): _description_
            name (str, optional): _description_. Defaults to None.
            value (str, optional): _description_. Defaults to None.

        Returns:
            EmbedField: _description_
        """

        return super().__new__(cls, name, value)


def wrap_message(message: str,
                 max_message_length: int = 2000,
                 wrapper: str = "",
                 header: str = ""):
    """_summary_

    Args:
        message (str): _description_
    """

    max_message_length = max_message_length - len(wrapper) - len(header)
    message_list = []
    message_itr_index = 0
    while message_itr_index < len(message):

        new_message = message[message_itr_index:message_itr_index +
                              max_message_length]
        newline_index = new_message.rfind("\n")

        if newline_index not in [0, -1] and (message_itr_index + len(new_message)) < len(message):
            new_message = message[message_itr_index:message_itr_index+newline_index+1]

        if wrapper != "":
            new_message = wrapper.format(
                new_message)
        message_list.append(f"{header}{new_message}")
        message_itr_index += len(new_message)
    return message_list


async def send_message(ctx: Context, message: str, header: str = "",
                       css: bool = False, wrapper: str = "",
                       reply: bool = True,
                       mention_author: bool = False):
    """_summary_

    Args:
        ctx (Context): _description_
        message (str): _description_
        header (str, optional): _description_. Defaults to None.
        css (bool, optional): _description_. Defaults to True.
        wrapper (str, optional): _description_. Defaults to "".
    """
    css_wrapper = "```css\n{}\n```"

    if header is None or header == "":
        header = f"{white_check_mark}\n"

    if css:
        wrapper = css_wrapper
    message_list = wrap_message(message, wrapper=wrapper, header=header)
    for message_instance in message_list:
        if reply:
            await ctx.reply(message_instance, mention_author=mention_author)
        else:
            await ctx.send(message_instance)


async def send_embed(ctx: Context,
                     embed_wrapper: EmbedWrapper = None,
                     embed: Embed = None,
                     reply: bool = True,
                     mention_author: bool = False,
                     embed_color: str = "green",
                     emoji: str = white_check_mark,
                     edit_message: Message = None,
                     file: File = None):
    """
    Send an embed Message containing `embed`. If an `embed_wrapper` is provided
        an embed will be constructed from it.


    Args:
        ctx (Context): _description_
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

    Returns:
        (list[Message] | Message): returns the messages generated to send the
            embeds
    """
    sent_file = file
    if not embed:
        color = MplColorHelper().get_unicode(embed_color)

        if embed_wrapper.duration is None:
            embed_wrapper.duration = time() - ctx.start_time
            embed_wrapper.create_footer()

        if not embed_wrapper.check_char_limit():
            embed_wrapper_list = embed_wrapper.split_embed()
        else:
            embed_wrapper_list = [embed_wrapper]
        message_list: list[Message] = []
        for current_embed_wrapper in embed_wrapper_list:
            embed = Embed(
                color=color,
                timestamp=datetime.fromtimestamp(time()))
            if (current_embed_wrapper.title == "" or
                    current_embed_wrapper.title is None):
                embed.title = f"{emoji} Success"
            elif emoji:
                embed.title = f"{emoji} {current_embed_wrapper.title}"
            else:
                embed.title = current_embed_wrapper.title
            embed.description = current_embed_wrapper.description
            embed.set_footer(text=current_embed_wrapper.footer)

            for embed_field in current_embed_wrapper.embed_fields:
                embed.add_field(name=embed_field.name,
                                value=embed_field.value)

            last_message = await _send_embed(
                ctx, embed, reply, edit_message, mention_author, file=sent_file)
            message_list.append(last_message)
            if sent_file is not None:
                sent_file = None
        if len(message_list) == 1:
            return message_list[0]
        else:
            return message_list
    return await _send_embed(ctx, embed, reply, edit_message, mention_author, file)


async def _send_embed(ctx: Context,
                      embed: Embed,
                      reply: bool,
                      edit_message: Message,
                      mention_author: bool,
                      file: File) -> Message:
    """
    Do the sending/editing of a message and return the response

    Args:
        ctx (Context): _description_
        embed (Embed): _description_
        reply (bool): _description_
        edit_message (Message): _description_
        mention_author (bool): _description_

    Returns:
        Message: _description_
    """
    if edit_message is not None:
        return await edit_message.edit(embed=embed)

    if reply:
        return await ctx.reply(embed=embed, mention_author=mention_author,
                               file=file)
    else:
        return await ctx.send(embed=embed, file=file)


async def send_embed_exception(ctx: Context, exception: MessageError, **kwargs):
    """_summary_

    Args:
        ctx (Context): _description_
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
