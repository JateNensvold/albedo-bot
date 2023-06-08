import asyncio
import pytest
import discord.ext.test as discord_test

from typing import TYPE_CHECKING

from albedo_bot.bot import AlbedoBot
import albedo_bot.config as config

from ...images.image_paths import LIGHTBEARER_ROSTER_PATH

from discord.ext import commands
from discord import Message


@pytest.fixture
def bot():
    # config.reload_loop(event_loop)
    bot = AlbedoBot()
    # discord_test.configure(bot)

    # print(f"loop {bot.loop}")
    # bot.loop = event_loop

    return bot


# @pytest.mark.asyncio
# async def test_async_client(bot: AlbedoBot):

    # @pytest.mark.asyncio
    # async def test_upload(bot: AlbedoBot):
    #     print(f"bot {bot}")

    #     sent_message = await discord_test.message(r"%help",
    #                                attachments=[LIGHTBEARER_ROSTER_PATH])

    #     print(sent_message.content)

    #     # message = discord_test.verify().message() #.contains().content("mock contents")
    #     # last_message = Message = discord_test.sent_queue.peek()

    #     # print(last_message)
