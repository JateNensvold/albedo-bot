from discord.ext import commands


def get_emoji(bot: commands.Bot, emoji_id: int):
    """_summary_

    Args:
        bot (commands.Bot): _description_
        emoji_id (int): _description_

    Returns:
        _type_: _description_
    """
    return bot.get_emoji(emoji_id)


class Emojies:
    """_summary_
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def get_emoji(self, emoji_id: int):
        """_summary_

        Args:
            emoji_name (str): _description_
        """
        return get_emoji(self.bot, emoji_id)
        # emoji = discord.utils.get(self.bot.emojis, name=emoji_name)
        # return emoji
