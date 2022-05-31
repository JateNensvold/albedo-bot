from typing import NamedTuple, Union

from discord.ext.commands.context import Context
from discord import Embed

from image_processing.utils.color_helper import MplColorHelper

from albedo_bot.utils.errors import MessageError
from albedo_bot.utils.emoji import red_x, white_check_mark


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
        """_summary_

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


def wrap_message(message: str, wrapper: str = "", header: str = ""):
    """_summary_

    Args:
        message (str): _description_
    """

    max_message_length = 2000 - len(wrapper) - len(header)
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
    message_list = wrap_message(message, wrapper, header)
    for message_instance in message_list:
        if reply:
            await ctx.reply(message_instance, mention_author=mention_author)
        else:
            await ctx.send(message_instance)


async def send_embed(ctx: Context,
                     embed_field_list: Union[list[EmbedField],
                                             EmbedField] = None,
                     embed: Embed = None,
                     reply: bool = True, mention_author: bool = False,
                     embed_color: str = "green",
                     emoji: str = white_check_mark):
    """_summary_

    Args:
        ctx (Context): _description_
        embed (Embed): _description_
    """
    if not embed:
        color = MplColorHelper().get_unicode(embed_color)
        embed = Embed(color=color)
        if not isinstance(embed_field_list, list):
            embed_field_list = [embed_field_list]
        for embed_field in embed_field_list:
            embed_name = embed_field.name
            if embed_name == "" or embed_name is None:
                embed_name = f"{emoji} Success"
            elif emoji:
                embed_name = f"{emoji} {embed_name}"

            embed.title = embed_name
            embed.description = embed_field.value
            # embed.add_field(name=embed_name, value=embed_field.value)
    if reply:
        await ctx.reply(embed=embed, mention_author=mention_author)
    else:
        await ctx.send(embed=embed)


async def send_embed_exception(ctx: Context, exception: MessageError, **kwargs):
    """_summary_

    Args:
        ctx (Context): _description_
        exception (MessageError): _description_
    """
    embed_fields = []

    if isinstance(exception, MessageError):
        exception_embed_fields = exception.embed_fields

        for exception_embed_field in exception_embed_fields:
            if exception_embed_field.name is None:
                embed_fields.append(
                    EmbedField(exception.__class__.__name__,
                               exception_embed_field.value))
            else:
                embed_fields.append(exception_embed_field)
    else:
        embed_fields.append(
            EmbedField(exception.__class__.__name__,
                       str(exception)))
    kwargs["embed_color"] = kwargs.get("embed_color", "red")
    kwargs["emoji"] = kwargs.get("emoji", red_x)

    await send_embed(ctx, embed_field_list=embed_fields, **kwargs)
