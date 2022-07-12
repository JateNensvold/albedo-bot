import itertools
import re
from typing import TYPE_CHECKING, Union

from discord.ext import commands as command_module

from albedo_bot.utils.message import EmbedWrapper, send_embed
from albedo_bot.utils.emoji import page_with_curl
from albedo_bot.utils.errors import DiscordPermissionError

if TYPE_CHECKING:
    from albedo_bot.bot import AlbedoBot


class HelpCog(command_module.MinimalHelpCommand):
    """_summary_

    Args:
        commands (_type_): _description_
    """

    def __init__(self):
        """_summary_
        """
        super().__init__()

        self.embed_color = None

    @property
    def bot(self) -> "AlbedoBot":
        """
        Get the currently running bot

        Returns:
            _type_: _description_
        """
        return self.context.bot

    def get_command_signature(self, command: command_module.Command):
        """_summary_

        Args:
            command (commands.Command): _description_
        """

        return f"{self.clean_prefix}{command.qualified_name} {command.signature}"

    # pylint: disable=unused-argument
    def get_category(self, command: command_module.core.Group, *args):
        """_summary_

        Args:
            command (commands.core.Group): _description_

        Returns:
            _type_: _description_
        """
        cog: command_module.Cog = command.cog
        if cog is not None:
            matches = re.split(r"Cog", cog.qualified_name)
            return matches[0]
        else:
            return f'\u200b{self.no_category}'

    # pylint: disable=dangerous-default-value
    def parse_command_help(self, command_help: str, remove_commands=["ctx"]):
        """_summary_

        Args:
            command_help (_type_): _description_
        """

        valid_help_lines = ValidHelpLines(ignore_whitespace=False)

        help_lines = command_help.splitlines()

        help_line_index = 0
        args_start_line = None

        while help_line_index < len(help_lines):
            help_line = help_lines[help_line_index]
            stripped_help_line = help_line.strip().lower()

            if "args:" in stripped_help_line and args_start_line is None:
                args_start_line = help_line_index
                valid_help_lines.add_line(help_line)
                help_line_index += 1
                valid_help_lines.add_highlighting = True
                valid_help_lines.ignore_whitespace = True
                continue
            elif len(stripped_help_line) == 0 and valid_help_lines.add_highlighting:
                valid_help_lines.add_highlighting = False
                valid_help_lines.ignore_whitespace = False
            for remove_command in remove_commands:
                break_remove = False
                if stripped_help_line.startswith(remove_command):
                    remove_help_line_index = help_line_index
                    remove_help_line = help_lines[remove_help_line_index]
                    lead_space_count = len(
                        remove_help_line) - len(remove_help_line.lstrip())
                    new_lead_space_count = -1
                    while (remove_help_line_index + 1) < len(help_lines) and lead_space_count != new_lead_space_count:
                        remove_help_line_index += 1
                        remove_help_line = help_lines[remove_help_line_index]
                        new_lead_space_count = len(
                            remove_help_line) - len(remove_help_line.lstrip())
                        help_line_index = remove_help_line_index

                    if lead_space_count == new_lead_space_count:
                        help_line_index -= 1
                    break_remove = True
                else:
                    valid_help_lines.add_line(help_line)
                if break_remove:
                    break
            help_line_index += 1
        return valid_help_lines.join("\n")

    def add_command_formatting(self,
                               command: Union[command_module.core.Group,
                                              command_module.core.Command]):
        """A utility function to format commands and groups.

        Parameters
        ------------
        command: :class:`Command`
            The command to format.
        """

        if command.description:
            self.paginator.add_line(command.description, empty=True)

        signature = self.get_command_signature(command)
        if command.aliases:
            self.paginator.add_line(signature)
            self.add_aliases_formatting(command.aliases)
        else:
            self.paginator.add_line(signature, empty=True)

        if command.help:

            try:
                new_command_help = self.parse_command_help(command.help)
                self.paginator.add_line(new_command_help, empty=True)
            except RuntimeError:
                for line in command.help.splitlines():
                    self.paginator.add_line(line)
                self.paginator.add_line()

    async def send_group_help(self, group: command_module.Group):
        can_run = await group.can_run(self.context)
        if not can_run:
            embed_wrapper = EmbedWrapper(
                title="Permissions Error",
                description=(
                    "If you believe you should have access to this command "
                    f"please contact the bot owner {self.bot.owner_id}"))
            raise DiscordPermissionError(embed_wrapper=embed_wrapper)

        return await super().send_group_help(group)

    async def send_bot_help(self, mapping: Union[
            dict[command_module.Cog, list[command_module.core.Group]], None]):
        """_summary_

        Args:
            mapping (_type_): _description_
        """

        ctx: command_module.Context = self.context
        bot: "AlbedoBot" = ctx.bot

        if bot.description:
            self.paginator.add_line(bot.description, empty=True)

        self.paginator.add_line(bot.help_description, empty=True)

        note = self.get_opening_note()
        if note:
            self.paginator.add_line(note, empty=True)

        filtered = await self.filter_commands(bot.commands, sort=True, key=self.get_category)
        to_iterate = itertools.groupby(filtered, key=self.get_category)

        for category, command_groups in to_iterate:
            command_groups = sorted(
                command_groups, key=lambda c: c.name) \
                if self.sort_commands else list(command_groups)
            self.add_bot_commands_formatting(command_groups, category)

        # pylint: disable=assignment-from-none
        note = self.get_ending_note()
        if note:
            self.paginator.add_line()
            self.paginator.add_line(note)

        await self.send_pages()

    async def send_pages(self):
        """_summary_
        """

        embed_color = self.embed_color or "white"

        for page in self.paginator.pages:

            await send_embed(
                self.context,
                embed_wrapper=EmbedWrapper(title=page_with_curl,
                                           description=page),
                emoji=None,
                embed_color=embed_color)
        self.embed_color = None


class ValidHelpLines:
    """
    Util class for keeping track of help text in function signatures
    """

    def __init__(self, ignore_whitespace: bool = True):
        """
        Set the initial value for `ignore_whitespace`

        Args:
            ignore_whitespace (bool, optional): Ignore all whitespace lines
                added to a ValidHelpLines Object while this is set to True.
                Defaults to True.
        """
        self.add_highlighting = False
        self.ignore_whitespace = ignore_whitespace
        self.valid_help_lines: list[str] = []

    def add_line(self, new_line: str, ignore_whitespace: bool = None):
        """
        Replaces all backtick(`) with a single quote('), also allow for
            customizing lines that are added to `valid_help_lines`

        Args:
            new_line (str): line getting added to `valid_help_lines`
            ignore_whitespace (bool, optional): Override for
                self.ignore_whitespace, that will supersedes whatever setting
                was set during initialization. Defaults to None.
        """

        new_line = new_line.replace("`", "'")

        if self.add_highlighting:
            whitespace_len = len(new_line) - len(new_line.lstrip())
            colon_index = new_line.find(":")
            if colon_index != -1:
                new_line = (f"{new_line[:whitespace_len]}"
                            f"`{new_line[whitespace_len:colon_index]}`"
                            f"{new_line[colon_index:]}")

        stripped_new_line = new_line.strip()
        if len(stripped_new_line) == 0:
            if ignore_whitespace is not None and ignore_whitespace:
                return
            elif self.ignore_whitespace:
                return

        self.valid_help_lines.append(new_line)

    def join(self, joining_delimiter: str):
        """
        Join together `valid_help_lines` into a single string

        Args:
            joining_delimiter (str): separator between each item in
                `valid_help_lines`

        Returns:
            str: Concatenation of valid_help_lines
        """

        return joining_delimiter.join(self.valid_help_lines)
