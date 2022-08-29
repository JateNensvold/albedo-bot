from typing import TYPE_CHECKING
from discord import File

from albedo_bot.utils.emoji import hourglass
from albedo_bot.utils.message.message_util import wrap_message

from albedo_bot.utils.embeds.embed_field import EmbedField


class EmbedWrapper:
    """
    A wrapper around a discord.py embed
    """

    def __init__(self, title: str = None,
                 description: str = "",
                 footer: str = "",
                 embed_fields: list[EmbedField] = None,
                 duration: float = None,
                 image: File = None,
                 multi_message_compatible: bool = True):
        """
        Creates the EmbedWrapper with the properties passed to it

        Args:
            title (str, optional): Title of embed. Defaults to None.
            description (str, optional): description text of embed.
                Defaults to "".
            footer (str, optional): footer text of embed.
                Default to "".
            embed_fields (list[EmbedField], optional):
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
            self.embed_fields: list[EmbedField] = []
        else:
            self.embed_fields = embed_fields
        self.footer = footer
        self.duration = duration
        self.create_footer()

        self.description = description
        self.image = image
        self.multi_message_compatible = multi_message_compatible

    def add_field(self, embed_field: EmbedField):
        """
        Add an EmbedField to the wrapper 

        Args:
            embed_field (EmbedField): field getting added
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

    def char_count(self):
        """
        Calculate the total number of characters in the EmbedWrapper object

        Returns:
            int: the character count of the EmbedWrapper object
        """
        fields = [self.title, self.description, self.footer]

        fields.extend([field.name for field in self.embed_fields])
        fields.extend([field.value for field in self.embed_fields])

        total = 0
        for item in fields:
            str_item = str(item) if str(item) != None else ''
            total += len(str_item)

        return total

    def check_char_limit(self):
        """
        Checks if the EmbedWrapper meets the total character limit and
        description character limits for a discord Embed

        Description Limit: 4096
        Total Limit: 6000

        Returns:
            bool: True when its under the character limit,
                False otherwise
        """

        if self.char_count() < 6000 and len(self.description) < 4096:
            return True
        return False

    def split_embed(self):
        """
        Split EmbedWrapper apart into multiple EmbedWrappers that each fit
        under the 6000 character text limit

        Ensures description length is under 4096 char

        *Does not validate length for title, footer or author entries.

        Returns:
            list[EmbedWrapper]: a list of EmbedWrappers that have been split 
                to be under the discord character limits for Embeds
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
        """
        Generate a string representation of the EmbedWrapper Object

        Returns:
            str: a string representation of the EmbedWrapper object
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
