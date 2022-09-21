from collections import deque
from albedo_bot.utils.errors import MessageSendError

from discord import Embed, Message, File
from discord.ext.commands.context import Context

from albedo_bot.utils.embeds.embed_wrapper import (
    MAX_EMBED_LENGTH, EmbedWrapper, MAX_EMBED_COUNT)
from albedo_bot.utils.embeds.select import SelectView
from albedo_bot.utils.message.message_util import (
    _send_message, wrap_message)
from albedo_bot.utils.embeds.embed_utils import generate_embeds

from albedo_bot.utils.emoji import white_check_mark

MAX_FILE_COUNT = 10

EMBED_ID = int
FILE_MAP = dict[EMBED_ID, list[File]]


class MessageWrapper:
    """
    Wraps the information needed for a discord message
    """

    def __init__(self,
                 ctx: Context,
                 text: str | None = None,
                 embed_wrappers: (list[EmbedWrapper] |
                                  EmbedWrapper |
                                  None) = None,
                 embeds: list[Embed] | Embed | None = None,
                 files: list[File] | None = None,
                 view: SelectView | None = None,
                 emoji: str = white_check_mark,
                 embed_color: str = "green"):
        """
        Initialize, parse and format all the data that gets sent in a discord
        Message. All data that exceeds maximum discord limits will be formatted
        across multiple messages

        Args:
            ctx (Context): invocation context containing information on how
                    a discord event/command was invoked
            text ( str | None): text to send in a message
            embed_wrapper (list[EmbedWrapper] | EmbedWrapper | None): embed
                wrapper(s) to turn into embeds. Defaults to None.
            embeds (list[Embed] | Embed | None): optional embed(s) that i
                 already created. Defaults to None.
            file (File | list[File]): File or list of files to send in message.
                Defaults to None.
            view (SelectView, optional): Discord view object to send in
                message(may contain selection or other discord embed types).
                Defaults to None.
            emoji (str, optional): Emoji to send in embed title.
                Defaults to white_check_mark.
            embed_color (str, optional): Color to set embeds while generating them.
                Defaults to "green".
        """

        if isinstance(files, File):
            self.files = [files]
        elif files is None:
            self.files = []

        self.text_list: list[str] = []
        if text is not None:
            self.text_list.extend(wrap_message(text))

        self.ctx = ctx
        self.view = view
        self._view = view

        file_map: FILE_MAP = {}
        embed_list = generate_embeds(ctx,
                                     file_map,
                                     embed_wrapper=embed_wrappers,
                                     embed=embeds,
                                     embed_color=embed_color,
                                     emoji=emoji)
        self.embed_list = embed_list
        self.file_map = file_map

    async def send(self, reply: bool, mention_author: bool):
        """
        Send all text, embeds, files and view associated with the
            MessageWrapper object

        Args:
            reply (bool): reply to the user who send the original message
            mention_author (bool): when replying to a user mention them when 
                this is true

        Returns:
            list[Message]: a list of the discord messages that were sent
        """

        sent_messages: list[Message] = []
        file_list = [*self.files]
        embed_queue = deque(self.embed_list)
        text_queue = deque(self.text_list)

        # These values are reset between message sends
        current_files: list[File] = []
        current_embeds: list[Embed] = []
        current_text = None

        while embed_queue or text_queue:
            if embed_queue:
                current_embed = embed_queue[0]
            else:
                current_embed = None

            if len(text_queue) > 1:
                current_text = text_queue.popleft()
                # Send messages up until the last text message
                sent_message = await self._send_message(
                    current_text, embeds=[], reply=reply,
                    mention_author=mention_author, files=[])
                sent_messages.append(sent_message)
                continue
            elif len(text_queue) > 0:
                # last text message to send
                current_text = text_queue.popleft()
            else:
                current_text = None

            if current_embed is None:
                break

            if len(current_embed) > MAX_EMBED_LENGTH:
                # Embed splitting is done in generate_embeds
                raise MessageSendError(
                    embed_wrapper=EmbedWrapper(
                        title="EmbedLength Error",
                        description=(
                            f"The following embed:\n{current_embed.title}\n"
                            f"has a length longer than {MAX_EMBED_LENGTH}.")))

            # Check if there is capacity to add an embed with files
            if id(current_embed) in self.file_map:
                embed_files = self.file_map[id(current_embed)]

                if len(embed_files) > MAX_FILE_COUNT:
                    # Embed files are added in generate_embeds
                    raise MessageSendError(
                        embed_wrapper=EmbedWrapper(
                            title="MaxFileCount Error",
                            description=(
                                f"The following embed:\n{current_embed.title}\n"
                                f"has more than {MAX_FILE_COUNT} files "
                                "associated with it.")))

                if (len(current_files) + len(embed_files) > MAX_FILE_COUNT):
                    # Send all current files to make space for new files,
                    #   should only exceed MAX_FILE_COUNT here from embed_files
                    #   filling up current_files
                    sent_message = await self._send_message(
                        text=current_text, embeds=current_embeds, reply=reply,
                        mention_author=mention_author, files=current_files)
                    sent_messages.append(sent_message)
                    current_files = []
                    current_embeds = []
                    continue

            # Check if there is capacity to add an embed
            if (self.message_len(current_embeds) +
                    self.embed_len(current_embed) > MAX_EMBED_LENGTH):
                # Send all current embeds to make space for the next embed
                sent_message = await self._send_message(
                    current_text, embeds=current_embeds, reply=reply,
                    mention_author=mention_author, files=current_files)
                sent_messages.append(sent_message)
                current_files = []
                current_embeds = []
                continue
            else:
                current_embeds.append(current_embed)
                embed_files = self.file_map.get(id(current_embed), None)
                if embed_files is not None:
                    current_files.extend(embed_files)
                embed_queue.popleft()

            if len(current_embeds) == MAX_EMBED_COUNT:
                if len(embed_queue) == 0:
                    self.fill_files(current_files, file_list)
                sent_message = await self._send_message(
                    text=current_text, embeds=current_embeds, reply=reply,
                    mention_author=mention_author, files=current_files)
                sent_messages.append(sent_message)
                current_files = []
                current_embeds = []

        self.fill_files(current_files, file_list)
        sent_message = await self._send_message(
            text=current_text, embeds=current_embeds, reply=reply,
            mention_author=mention_author, files=current_files)
        sent_messages.append(sent_message)
        current_files = []
        current_embeds = []

        while file_list:
            # Modify file_list in place
            self.fill_files(current_files, file_list)
            sent_message = await self._send_message(
                text=None, embeds=None, reply=reply,
                mention_author=mention_author, files=current_files)
            sent_messages.append(sent_message)
            current_files = []

        return sent_messages

    async def _send_message(self, text: str | None, embeds: list[Embed],
                            reply: bool, mention_author: bool, files: list[File]):
        """
        A wrapper around calling the _send_message helper, also handles 
        clearing data that was initialized in the MessageWrapper that should
        only be sent once

        Args:
            text (str | None): text to send in message
            embeds (list[Embed]): embeds to send in message
            reply (bool): reply to the user who send the original message
            mention_author (bool): when replying to a user mention them when 
                this is true
            files (list[File]): files to send in message

        Returns:
            Message: message sent in discord
        """
        sent_message = await _send_message(
            content=text, ctx=self.ctx, embeds=embeds, reply=reply,
            mention_author=mention_author, view=self.view,
            files=files)
        # Clear the view after it has been sent so it only gets sent once
        if self._view:
            self._view = None
        return sent_message

    @staticmethod
    def fill_files(current_files: list[File], extra_files: list[File]):
        """
        Pul files off of  extra_files and add them to current_files until the 
        length of current_files is equal to MAX_FILE_COUNT or extra_files runs 
        out of files to add

        *both current_files and extra_files will be modified in place

        Args:
            current_files (list[File]): file list to add files to
            extra_files (list[File]): file list to remove files from
        """
        if len(extra_files) == 0:
            return current_files

        file_count = len(current_files)
        if file_count < MAX_FILE_COUNT:
            file_list_space = MAX_FILE_COUNT - file_count
            current_files.extend(extra_files[:file_list_space])
            # Remove added files from extra_files
            del extra_files[:file_list_space]

        return current_files

    @staticmethod
    def embed_len(embed: Embed):
        """
        Find the length of text inside an embed

        Args:
            embed (Embed): embed to find length of

        Returns:
            int: length of text in embed
        """

        fields = [embed.title, embed.description,
                  embed.footer.text, embed.author.name]

        fields.extend([field.name for field in embed.fields])
        fields.extend([field.value for field in embed.fields])

        embed_total = 0
        for item in fields:
            embed_total += len(str(item)) if item is not None else 0
        # print(embed.title, embed_total)

        return embed_total

    @staticmethod
    def message_len(embed_list: list[Embed]):
        """
        Calculate the total length of the information that would get sent 
        from embed_list

        Returns:
            int: total length of text
        """

        message_total = 0
        for embed in embed_list:
            message_total += MessageWrapper.embed_len(embed)
        return message_total
