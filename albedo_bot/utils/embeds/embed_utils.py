
from datetime import datetime
from time import time

from discord.ext.commands.context import Context
from discord import Embed, File
from image_processing.utils.color_helper import MplColorHelper

from albedo_bot.utils.emoji import white_check_mark
from albedo_bot.utils.embeds.embed_wrapper import EmbedWrapper


def generate_embeds(ctx: Context,
                    file_map: dict[int, list[File]],
                    embed_wrapper: EmbedWrapper | list[EmbedWrapper] = None,
                    embed: list[Embed] | Embed = None,
                    embed_color: str = "green",
                    emoji: str = white_check_mark):
    """
    Take a list of embed and embed_wrapper and generate all the embeds for a
    message in a list

    *Edit's file_map in place when embeds contain images

    Args:
        ctx (Context): _description_
        file_map (dict[str, list[File]]): an empty dictionary that can be
            updated  with a mapping of embeds to files that need to get send 
            in the same message as the embed
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
    if isinstance(embed, list):
        for _embed in embed:
            embed_list.append(_embed)
    elif embed is not None:
        embed_list.append(embed)

    color = MplColorHelper().get_unicode(embed_color)

    if isinstance(embed_wrapper, list):
        _embed_wrappers = embed_wrapper
    elif isinstance(embed_wrapper, EmbedWrapper):
        _embed_wrappers = [embed_wrapper]
    else:
        _embed_wrappers = []

    embed_wrapper_list: list[EmbedWrapper] = []
    # Initialize any uninitialized content in the embed_wrappers and break
    #   apart the content to fit inside the embed character limits
    for _embed_wrapper in _embed_wrappers:
        if _embed_wrapper.duration is None:
            _embed_wrapper.duration = (
                time() - ctx.message.created_at.timestamp())
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
            if current_embed.title not in file_map:
                file_map[id(current_embed)] = []
            file_map[id(current_embed)].append(current_embed_wrapper.image)

        embed_list.append(current_embed)
    return embed_list
