import asyncio

from albedo_bot.utils.hero_data import HeroData
from albedo_bot.utils.permissions import Permissions
from albedo_bot.database.database import Database
from albedo_bot.utils.config import Config
from image_processing.processing.async_processing \
    .async_processing_client import (AsyncProcessingClient)

from .json_configs import (
    PERMISSIONS_JSON_PATH, DATABASE_CONFIG_JSON_PATH, PREFIX_JSON_PATH,
    BLACKLIST_JSON_PATH, HERO_ALIAS_JSON_PATH, HERO_JSON_PATH)


class ConfigObjects:
    def __init__(self) -> None:
        self.permissions = Permissions.from_json(
            PERMISSIONS_JSON_PATH.resolve())
        self._database_config: Config = None
        self._database: Database = None
        self._hero_data: HeroData = None
        self._prefixes: Config = None
        self._blacklist: Config = None
        self._hero_alias: Config = None
        self.processing_client = AsyncProcessingClient()

    @property
    def database_config(self):
        return self._database_config

    @property
    def database(self):
        return self._database

    @property
    def hero_data(self):
        return self._hero_data

    @property
    def prefixes(self):
        return self._prefixes

    @property
    def blacklist(self):
        return self._blacklist

    @property
    def hero_alias(self):
        return self._hero_alias

    def reload_loop(self, event_loop):
        """
        Reload all loop based objects to use a new event loop.

        Args:
            event_loop (Any): An event loop implementation to pass to the
                loop objects
        """

        self._database_config = Config(DATABASE_CONFIG_JSON_PATH.resolve(),
                                       loop=event_loop)
        self._database = Database.from_json(self._database_config)
        self._hero_data = HeroData(HERO_JSON_PATH.resolve(),
                                   loop=event_loop)
        self._prefixes = Config(PREFIX_JSON_PATH.resolve(),
                                loop=event_loop)
        self._blacklist = Config(BLACKLIST_JSON_PATH.resolve(),
                                 loop=event_loop)
        self._hero_alias = Config(HERO_ALIAS_JSON_PATH.resolve(),
                                  loop=event_loop)
