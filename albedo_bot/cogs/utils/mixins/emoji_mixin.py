
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from albedo_bot.bot import AlbedoBot


class EmojiMixin:
    """
    A mixin that implements utility commands for interacting with emojis 
    """

    bot: "AlbedoBot"

    def get_emoji(self, emoji_name: str):
        """
        Fetch an emoji by name

        Args:
            emoji_name (str): name of emoji to get
        """
        try:
            return self.bot.emoji_cache[emoji_name]
        except KeyError:
            raise Exception("Unable to find an emoji with the name "
                            f"({emoji_name})") from KeyError
