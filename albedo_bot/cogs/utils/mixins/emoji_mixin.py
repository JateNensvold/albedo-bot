
from typing import TYPE_CHECKING

import discord

if TYPE_CHECKING:
    from albedo_bot.bot import AlbedoBot


class EmojiMixin:
    """_summary_
    """

    bot: "AlbedoBot"

    def get_emoji(self, emoji_name: str):
        """_summary_

        Args:
            emoji_name (str): _description_
        """
        try:
            return self.bot.emoji_cache[emoji_name]
        except KeyError:
            raise Exception("Unable to find an emoji with the name "
                            f"({emoji_name})") from KeyError
