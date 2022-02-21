import os
import json
from typing import Dict
# Import commands so bot will register all commands
from albedo_bot.commands.base import bot, session
import albedo_bot.commands  # pylint: disable=unused-import
# client = discord.Client()
TOKEN = os.getenv('TOKEN')
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
CONFIG_DATA: Dict = None

# @client.event
# async def on_message(message):
#     if not message.guild:
#         await message.channel.send('this is a dm')
# print(TOKEN)


# @CLIENT.event
# async def on_ready():
#     """[summary]
#     """
#     print(f"We have logged in as {CLIENT.user}")


# @client.event
# async def on_message(message: discord.Message):
#     """[summary]

#     Args:
#         message ([type]): [description]
#     """
#     # print(message)
#     # await message.channel.send('Hello!')
#     # if message.author == CLIENT.user:
#     #     return

#     print(message)

#     if message.content.startswith('$hello'):
#         await message.channel.send('Hello!')


class ConfigData:
    """[summary]
    """

    def __init__(self, file_path: str):
        """[summary]

        Args:
            file_path (str): [description]
        """
        self.data = {}
        self.read_config(file_path)
        self.file_path = file_path

    def read_config(self, config_path: str):
        """[summary]
        """

        with open(config_path, "r", encoding="utf-8") as file:
            self.data = json.load(file)

    def write_config(self):
        """[summary]
        """
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(self.data, file)

    def __enter__(self):
        """
        """

        return self

    def __exit__(self,  _exc_type, _exc_value, _traceback):
        """[summary]
        """
        session.flush()


def main():
    """[summary]
    """

    config_path = os.path.join(os.path.dirname(DIR_PATH), "guild_config.json")
    with ConfigData(config_path) as data:
        global CONFIG_DATA  # pylint: disable=global-statement
        CONFIG_DATA = data
        bot.run(TOKEN)


if __name__ == "__main__":
    main()
