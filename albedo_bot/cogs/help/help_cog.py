
import itertools
import re
from typing import NamedTuple, TYPE_CHECKING

from discord.ext import commands

from albedo_bot.utils.message import EmbedField, send_embed
from albedo_bot.utils.emoji import page_with_curl

if TYPE_CHECKING:
    from albedo_bot.bot import AlbedoBot


class CommandSummary(NamedTuple):
    """_summary_

    Args:
        NamedTuple (_type_): _description_
    """
    command_name: str
    summary: str


class HelpCog(commands.MinimalHelpCommand):
    """_summary_

    Args:
        commands (_type_): _description_
    """

    def get_command_signature(self, command: commands.Command):
        """_summary_

        Args:
            command (commands.Command): _description_
        """

        return f"{self.clean_prefix}{command.qualified_name} {command.signature}"

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

    async def send_bot_help(self, mapping: dict[
            commands.Cog, list[commands.core.Group]]):
        """_summary_

        Args:
            mapping (_type_): _description_
        """

        ctx: commands.Context = self.context
        bot: "AlbedoBot" = ctx.bot

        if bot.description:
            self.paginator.add_line(bot.description, empty=True)

        note = self.get_opening_note()
        if note:
            self.paginator.add_line(note, empty=True)

        filtered = await self.filter_commands(bot.commands, sort=True, key=self.get_category)
        to_iterate = itertools.groupby(filtered, key=self.get_category)

        for category, command_groups in to_iterate:
            command_groups = sorted(
                command_groups, key=lambda c: c.name) if self.sort_commands else list(command_groups)
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

        for page in self.paginator.pages:
            await send_embed(
                self.context,
                embed_field_list=EmbedField(name=page_with_curl,
                                            value=page),
                emoji=None,
                embed_color="white")
