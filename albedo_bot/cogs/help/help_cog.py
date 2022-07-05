
import itertools
import re
from typing import TYPE_CHECKING, Union

from discord.ext import commands

from albedo_bot.utils.message import EmbedField, send_embed
from albedo_bot.utils.emoji import page_with_curl

if TYPE_CHECKING:
    from albedo_bot.bot import AlbedoBot


class HelpCog(commands.MinimalHelpCommand):
    """_summary_

    Args:
        commands (_type_): _description_
    """

    def __init__(self):
        """_summary_
        """
        super().__init__()

        self.embed_color = None

    def get_command_signature(self, command: commands.Command):
        """_summary_

        Args:
            command (commands.Command): _description_
        """

        return f"{self.clean_prefix}{command.qualified_name} {command.signature}"

    # pylint: disable=unused-argument
    def get_category(self, command: commands.core.Group, *args):
        """_summary_

        Args:
            command (commands.core.Group): _description_

        Returns:
            _type_: _description_
        """
        cog: commands.Cog = command.cog
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

        valid_help_lines = []

        help_lines = command_help.splitlines()

        help_line_index = 0
        while help_line_index < len(help_lines):
            help_line = help_lines[help_line_index]
            stripped_help_line = help_line.strip().lower()

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
                    valid_help_lines.append(help_line)
                if break_remove:
                    break
            help_line_index += 1
        return "\n".join(valid_help_lines)

    def add_command_formatting(self, command: Union[commands.core.Group, commands.core.Command]):
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

    async def send_bot_help(self, mapping: Union[dict[
            commands.Cog, list[commands.core.Group]], None]):
        """_summary_

        Args:
            mapping (_type_): _description_
        """

        ctx: commands.Context = self.context
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
                embed_field_list=EmbedField(name=page_with_curl,
                                            value=page),
                emoji=None,
                embed_color=embed_color)
        self.embed_color = None
