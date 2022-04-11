import asyncio
import json
from typing import Any, Dict, List

import sqlalchemy
from sqlalchemy.engine.cursor import CursorResult
from sqlalchemy.engine.result import MappingResult
from sqlalchemy.ext.asyncio import (
    create_async_engine, AsyncEngine, AsyncSession)
from sqlalchemy.orm import Session

# While importing base, it imports all schema in albedo_bot.database.schema
#   that need to be imported before calls to create_tables
from albedo_bot.database.schema import base
from albedo_bot.config.hero_data import HeroData
import albedo_bot.config as config


class Database:
    """[summary]
    """

    def __init__(self, user: str, password: str, address: str,
                 database_name: str = "postgres"):
        """[summary]

        Args:
            user (str): [description]
            password (str): [description]
            address (str): [description]
            database_name (str, optional): [description]. Defaults to "postgres".
        """
        self.user = user
        self.password = password
        self.address = address
        self.database_name = database_name
        self.engine: AsyncEngine = None
        self.session: Session = None

        self.base = base.Base
        self.metadata: sqlalchemy.MetaData = self.base.metadata

        self.postgres_connect()

    @classmethod
    def from_json(cls, json_path):
        """_summary_

        Args:
            json_path (_type_): _description_
        """

        with open(json_path, "r", encoding="utf-8") as config_file:
            database_config = json.load(config_file)
            database = Database(database_config["user"], database_config["password"],
                                database_config["address"])

        return database

    def postgres_connect(self, user: str = None, password: str = None,
                         address: str = None, database_name: str = None,
                         autoflush: bool = True,
                         db_string: str = None):
        """[summary]

        Args:
            user (str): [description]
            password (str): [description]
            address (str): [description]
            database_name ([type]): [description]
        """
        if user:
            self.user = user
        if password:
            self.password = password
        if address:
            self.address = address
        if database_name:
            self.database_name = database_name

        if db_string is None:
            db_string = (
                f"postgresql+asyncpg://{self.user}:{self.password}@{self.address}/"
                f"{self.database_name}")
        print(db_string)
        self.engine: AsyncEngine = create_async_engine(
            db_string)  # connect to server

        self.session = AsyncSession(
            self.engine, autoflush=autoflush)

    def session_callback(self, *args, **kwargs):
        """_summary_
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._session_callback(*args, **kwargs))

    async def _session_callback(self, sql_object: Any,
                                update: bool = True) -> Any:
        """_summary_

        Args:
            session (Session): _description_
            object (Any): _description_

        Returns:
            Any: _description_
        """
        async with self.session as session:
            async with session.begin():
                self.session.add(sql_object)
            await self.session.flush()
            if update:
                await self.session.refresh(sql_object)

    async def init_database(self, database_name: str, raise_error: bool = True):
        """
        Creates a database with the current connection under the name
        'database_name'. If a database of that name already exists an exception
        will get raised when 'raise_error' is True, otherwise the existing
        database will be selected

        Args:
            database_name (str): new database name
        """
        if database_name not in await self.list_database():
            async with self.session as session:
                await self.session.execute("commit")
                await self.session.execute(f'CREATE DATABASE "{database_name}"')

        else:
            if raise_error:
                raise Exception((
                    f"Database with the name '{database_name}' already exists. "
                    "Choose a new name or delete the existing database before "
                    "creating a new one"))
        self.select_database(database_name)

        await self.create_tables()

        # Load all hero data into database
        hero_data = HeroData.from_json(
            config.HERO_JSON_PATH, self._session_callback)
        await hero_data.build()

    async def drop_database(self, database_name: str):
        """_summary_

        Args:
            database_name (str): _description_
        """
        db_string = (
            f"postgresql+asyncpg://{self.user}:{self.password}@{self.address}")
        self.postgres_connect(db_string=db_string)

        async with self.session as session:
            await self.session.execute("commit")
            await self.session.execute(f"drop database {database_name}")

    def select_database(self, database_name: str):
        """[summary]

        Args:
            database_name (str): [description]
        """
        self.postgres_connect(self.user, self.password,
                              self.address, database_name)

    async def create_tables(self):
        """
        Creates all the database Tables defined by albedo_bot
        """
        self.base.metadata.bind = self.engine

        async with self.engine.begin() as conn:
            # await conn.run_sync(self.base.metadata.drop_all)
            await conn.run_sync(self.base.metadata.create_all)
        # self.base.metadata.create_all(self.engine)

    async def list_database(self):
        """[summary]
        """

        async with self.session as session:
            session_result: CursorResult = await self.session.execute(
                'SELECT datname FROM pg_database;')
            database_tuples: List[Dict[str, str]
                                  ] = session_result.mappings().all()

        database_list = [db_dict["datname"] for db_dict in database_tuples]
        return database_list

    def list_tables(self):
        """[summary]
        """
        inspector = sqlalchemy.inspect(self.engine)
        tables = inspector.get_table_names()
        return tables
