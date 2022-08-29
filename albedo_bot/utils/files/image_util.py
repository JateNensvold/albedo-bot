from typing import NamedTuple
from albedo_bot.utils.errors import MessageError
from albedo_bot.utils.message.message_send import EmbedWrapper


SITE_PREFIX = "https://cdn.discordapp.com"
IMAGE_EXTENSION_TYPES: list[str] = ["jpg", "jpeg", "png"]


class ContentType(NamedTuple):
    """
    A class to represent File ContentTypes
    """
    file_type: str
    extension_type: str

    @classmethod
    def from_str(cls, content_type: str):
        """
        Create a ContentType class from a discord.py content_type str

        Args:
            content_type (str): content_type string
        """

        file_type, extension_type = content_type.split("/")
        return ContentType(file_type, extension_type)


def valid_image(image_url: str, content_type: ContentType):
    """
    Checks if image_url is discord image

    Args:
        image_url (str): url to image
        extension_type (str): extension type of image
    """
    return valid_url(image_url) and valid_extension(
        image_url, content_type.extension_type)


def valid_url(image_url: str):
    """
    Check if an image_url is from discord

    Args:
        image_url (str): url to image
    """
    if image_url.startswith(SITE_PREFIX):
        return True
    embed_wrapper = EmbedWrapper(
        title="Invalid image url",
        description=(
            f"The following attachment is invalid "
            f"{image_url}, all attachments must come from {SITE_PREFIX}"))
    raise MessageError(embed_wrapper=embed_wrapper)


def valid_extension(image_url: str, extension_type: str):
    """
    Check if an extension type is valid for a discord image

    Args:
        extension_type (str): extension type of image
    """
    if extension_type.lower() in IMAGE_EXTENSION_TYPES:
        return True
    embed_wrapper = EmbedWrapper(
        title="Invalid file type",
        description=(
            f"The following attachment is invalid "
            f"{image_url}, Image uploads only support "
            f"the following file types `{', '.join(IMAGE_EXTENSION_TYPES)}`"))
    raise MessageError(embed_wrapper=embed_wrapper)
