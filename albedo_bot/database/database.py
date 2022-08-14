import asyncio
import json
from typing import Any, Callable, Dict, List

import sqlalchemy
from sqlalchemy.engine.cursor import CursorResult
from sqlalchemy.ext.asyncio import (
    create_async_engine, AsyncEngine, AsyncSession, async_scoped_session)
from sqlalchemy.orm import sessionmaker


# While importing base, it imports all schema in albedo_bot.database.schema
#   that need to be imported before calls to create_tables ensuring that all
#   database schema are created
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

        self.base = base.Base
        self.metadata: sqlalchemy.MetaData = self.base.metadata

        self.session_factory = None
        self.session_producer = None

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
            database.select_database(database_config["name"])

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

        self.session_factory = sessionmaker(
            self.engine, autoflush=autoflush, expire_on_commit=False,
            class_=AsyncSession)

        self.session_producer = async_scoped_session(
            self.session_factory, self.startup_scope)

    def startup_scope(self):
        """_summary_

        Raises:
            Exception: _description_
            Exception: _description_

        Returns:
            _type_: _description_
        """
        return self.engine.url

    @property
    def session(self) -> AsyncSession:
        """_summary_
T
        Returns:
            : _description_
        """
        return self.session_producer()

    def update_scoped_session(self, scope_func: Callable):
        """_summary_

        Args:
            scope_func (Callable): _description_
        """
        self.session_producer = async_scoped_session(
            self.session_factory, scope_func)

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
        async with self.session:
            async with self.session.begin():
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
            async with self.session:
                await self.session.execute("commit")
                await self.session.execute(f'CREATE DATABASE "{database_name}"')

        else:
            if raise_error:
                raise Exception((
                    f"Database with the name '{database_name}' already exists. "
                    "Choose a new name or delete the existing database before "
                    "creating a new one"))
        self.select_database(database_name)

        await self._init_tables()
        await self._load_data()
        # Load all hero data into database

    async def _load_data(self):
        """_summary_
        """
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

        database_list = await self.list_database()
        if database_name not in database_list:
            raise Exception(f"'{database_name}' is not a valid database name, "
                            f"({database_list})")
        if not self._confirm_action(f"delete '{database_name}'"):
            return
        async with self.session:
            await self.session.execute("commit")
            await self.session.execute(f"drop database {database_name}")
        print(f"Database {database_name} dropped.")

    def _confirm_action(self, action_str: str):
        """_summary_

        Args:
            action_str (str): _description_

        Returns:
            _type_: _description_
        """
        print(f"You are about to {action_str}. Enter 'Yes' to continue "
              "or any other key to stop")
        key_input = input()
        if key_input.lower() == "yes":
            return True
        print(f"{action_str} aborted.")
        return False

    def select_database(self, database_name: str):
        """[summary]

        Args:
            database_name (str): [description]
        """
        self.postgres_connect(database_name=database_name)

    async def _init_tables(self):
        """
        Creates all the database Tables defined by albedo_bot
        """
        self.base.metadata.bind = self.engine

        print(f"Initializing tables in '{self.database_name}'")
        async with self.engine.begin() as conn:
            await conn.run_sync(self.base.metadata.create_all)

    async def _drop_tables(self, check_action: bool = True):
        """_summary_
        """

        if check_action and not self._confirm_action(f"drop tables in '{self.database_name}'"):
            return

        self.base.metadata.bind = self.engine

        async with self.engine.begin() as conn:
            await conn.run_sync(self.base.metadata.drop_all)

    async def reset_database(self):
        """_summary_
        """
        if not self._confirm_action(f"reset tables in '{self.database_name}'"):
            return
        await self._drop_tables(check_action=False)
        await self._init_tables()
        await self._load_data()

    async def list_database(self):
        """[summary]
        """

        async with self.session:
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
