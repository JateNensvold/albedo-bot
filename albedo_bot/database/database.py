import os
import subprocess
from pathlib import Path
from typing import Any, Callable, Dict, List

import sqlalchemy
import asyncio
from sqlalchemy.engine.cursor import CursorResult
from sqlalchemy.ext.asyncio import (
    create_async_engine, AsyncEngine, AsyncSession, async_scoped_session)
from sqlalchemy.orm import sessionmaker


# While importing base, it imports all schema in albedo_bot.database.schema
#   that need to be imported before calls to create_tables ensuring that all
#   database schema are created
from albedo_bot.database.schema import base
from albedo_bot.utils.hero_data import HeroData
from albedo_bot.utils.config import Config
from albedo_bot.utils.errors import DatabaseError

import albedo_bot.config as config


class Database:
    """
    Database class that is used to manage database creation, initialization,
        deletion and sessions
    """

    def __init__(self, user: str, password: str, address: str,
                 database_name: str = "postgres",
                 port: str = "5432"):
        """        
        Initialize all database connection values and connect to the database

        Args:
            user (str): username to connect to database with
            password (str): password to connect to database with
            address (str): address of database to connect to
            database_name (str, optional): name of database to connect to. 
                Defaults to "postgres".
            port (str, optional): port the database cluster is accepting 
                connections on. Defaults to "5432".
        """
        self.user = user
        self.password = password
        self.address = address
        self.database_name = database_name
        self.port = port
        self.engine: AsyncEngine = None

        self.base = base.Base
        self.metadata: sqlalchemy.MetaData = self.base.metadata

        self.session_factory = None
        self.session_producer = None

        self.postgres_connect()

    @classmethod
    def from_json(cls, database_config: Config):
        """
        Create the database from a database_config file

        Args:
            database_config (Config): Config file object with all the needed
                database information

        Returns:
            Database: a fully initialized and connected database object
        """
        database = Database(
            config.DATABASE_USER,
            config.DATABASE_PASS,
            database_config["address"])
        database.select_database(database_config["name"])

        return database

    def postgres_connect(self, user: str = None, password: str = None,
                         address: str = None, database_name: str = None,
                         autoflush: bool = True,
                         db_string: str = None):
        """
        Connect to a postgres database

        Args:
            user (str): username to connect to database with.
                Defaults to None
            password (str): password to connect to database with.
                Defaults to None
            address (str): address database is at.
                Defaults to None
            database_name (str): name of database to connect to.
                Defaults to None
            autoflush (bool, optional): flag telling the database engine to
                autoflush to the database or not. Defaults to True.
            db_string (str, optional): A fully formed database connection
                string that can be used to connect to a database.
                Defaults to None.
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
        """
        Create/return a new session for the current scope

        Returns:
            : _description_
        """
        return self.session_producer()

    def update_scoped_session(self, scope_func: Callable):
        """
        Update the session producer to use a new scope_func to determine
            session lifecycle

        Args:
            scope_func (Callable): _description_
        """
        self.session_producer = async_scoped_session(
            self.session_factory, scope_func)

    def session_callback(self, *args, **kwargs):
        """
        Call the session callback from non async code
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._session_callback(*args, **kwargs))

    async def _session_callback(self,
                                sql_object: Any,
                                update: bool = True) -> Any:
        """
        Add a new object to the database

        Args:
            sql_object (Any): object to add to database
            update (bool, optional): Flag to refresh all references to the
                object in memory. Defaults to True.
        """
        async with self.session:
            async with self.session.begin():
                self.session.add(sql_object)
            await self.session.flush()
            if update:
                await self.session.refresh(sql_object)

    async def init_database(self, database_name: str,
                            hero_data: HeroData,
                            portrait_folders: list[Path],
                            raise_error: bool = True,):
        """
        Creates a database with the current connection under the name
        'database_name'. If a database of that name already exists an exception
        will get raised when 'raise_error' is True, otherwise the existing
        database will be selected

        Args:
            database_name (str): new database name
            hero_data (HeroData): data to initialize database with
            portrait_folders (list[Path]): list of paths to folders
                containing hero portraits
            raise_error (bool, optional): Flag to raise an error when the
                database being initialized already exists. Defaults to True.
        Raises:
            DatabaseError: raised when a database with database_name already
                exists
        """
        if database_name not in await self.list_database():
            async with self.session:
                await self.session.execute("commit")
                await self.session.execute(
                    f'CREATE DATABASE "{database_name}"')

        else:
            if raise_error:
                raise DatabaseError((
                    f"Database with the name '{database_name}' already exists. "
                    "Choose a new name or delete the existing database before "
                    "creating a new one"))
        self.select_database(database_name)

        # Load all hero data into database
        await self._init_tables()
        await self._load_data(hero_data, portrait_folders)
        # Commit transaction to database and remove connection
        await self.session_producer.commit()
        await self.session_producer.flush()
        await self.session_producer.remove()

    async def _load_data(self, hero_data: HeroData,
                         portrait_folders: list[Path]):
        """
        Load HeroData into the database

        Args:
            hero_data (HeroData): data to initialize database with
            portrait_folders (list[Path]): list of paths to folders
                containing hero portraits
        """
        await hero_data.build(self.session, portrait_folders)

    async def drop_database(self, database_name: str):
        """
        Delete/drop a database

        Args:
            database_name (str): name of database to drop
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
        """
        A generic template that prompts the user to confirm an action

        Args:
            action_str (str): action to prompt for

        Returns:
            bool: true if user confirmed the action, false otherwise
        """
        print(f"You are about to {action_str}. Enter 'Yes' to continue "
              "or any other key to skip")
        key_input = input()
        if key_input.lower() == "yes":
            return True
        print(f"{action_str} aborted.")
        return False

    def select_database(self, database_name: str):
        """
        Select/Connect to a new database in a database cluster

        Args:
            database_name (str): name of database to connect with
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
        """
        Drop all tables in the current database

        Args:
            check_action (bool, optional): Flag to prompt the user to
                confirm they want to drop the tables. Defaults to True.
        """
        if (check_action and
                not self._confirm_action(
                    f"drop tables in '{self.database_name}'")):
            return

        self.base.metadata.bind = self.engine

        async with self.engine.begin() as conn:
            await conn.run_sync(self.base.metadata.drop_all)

    async def reset_database(self, hero_data: HeroData,
                             portrait_folders: list[Path]):
        """
        Reset a database by dropping all the tables and then
            re-initializing the database with the default data
        """
        if not self._confirm_action(f"reset tables in '{self.database_name}'"):
            return
        await self._drop_tables(check_action=False)
        await self._init_tables()
        await self._load_data(hero_data, portrait_folders)

    async def list_database(self):
        """
        List all the databases in a cluster
        """
        async with self.session:
            session_result: CursorResult = await self.session.execute(
                'SELECT datname FROM pg_database;')
            database_tuples: List[Dict[str, str]
                                  ] = session_result.mappings().all()

        database_list = [db_dict["datname"] for db_dict in database_tuples]
        return database_list

    def list_tables(self):
        """
        List all the tables for a database
        """
        inspector = sqlalchemy.inspect(self.engine)
        tables = inspector.get_table_names()
        return tables

    async def backup_database(self, backup_location: str):
        """
        Runs the backup command in a subprocess to backup the database

        Args:
            backup_location (str): location to generate backup files at

        Returns:
            str: returns output of backup subprocess

        Raises:
            SubprocessError: raised when any of the crontab subprocess
                commands fail or return a nonzero exit code
        """

        self._generate_pgpass()

        backup_db_directory = Path(__file__).parent.parent.parent
        backup_command_path = backup_db_directory.joinpath("backup_db")
        backup_command_args = ["bash", str(backup_command_path),
                               backup_location, self.database_name, self.user]

        await self.generate_cron(backup_command_args)

        backup_output = subprocess.run(
            backup_command_args, shell=False, text=True, check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

        return f"Out: {backup_output.stdout}\nErr: {backup_output.stderr}"

    async def generate_cron(self, backup_command_args: list[str]):
        """
        Generates the crontab entry needed to backup the database

        Args:
            backup_command_args (list[str]): list of args used to run the
                database backup command

        Raises:
            SubprocessError: raised when any of the crontab subprocess
                commands fail or return a nonzero exit code
        """

        backup_configured = config.database_config.get(
            "database_backup_configured", False)
        if backup_configured:
            return
        print(("You have not setup daily cron backups for your database. "
               "Confirm the following prompt if you wish to automatically "
               "setup cron daily backups"))
        generate_cron = self._confirm_action(
            "enable database backups through cron")
        if not generate_cron:
            return

        cron_frequency = "0 0 * * *"
        cron_command = f"{cron_frequency} {' '.join(backup_command_args)}"

        crontab_list_command = ["crontab", "-l"]

        crontab_list_contents = subprocess.run(
            crontab_list_command, shell=False, text=True, check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

        cron_tab_commands = crontab_list_contents.stdout
        if cron_command not in cron_tab_commands:
            cron_tab_commands = f"{cron_tab_commands}{cron_command}\n"

        update_crontab_command = ["crontab", "-"]

        update_crontab_output = subprocess.run(
            update_crontab_command, shell=False, text=True, check=True,
            input=cron_tab_commands,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        await config.database_config.put("database_backup_configured", True)

        print((f"Out: [{update_crontab_output.stdout}]\nErr: "
               f"[{update_crontab_output.stderr}]"))

    def _generate_pgpass(self):
        """
        Generate the .pgpass file that allows pg_dump to be run without a
            password getting passed to it
        """
        pg_pass_str = (f"{self.address}:{self.port}:{self.database_name}:"
                       f"{self.user}:{self.password}")

        # pg_file_path = "~/.pgpass"
        pg_file_path = Path.home().joinpath(".pgpass")

        file_exists = False
        file_mode = "w"
        if os.path.exists(pg_file_path):
            # Open in read+ mode so we can read once then append to the end of
            #   the file
            file_exists = True
            file_mode = "r+"

        with open(pg_file_path, file_mode, encoding="utf-8") as pg_pass_file:
            if file_exists:
                pg_pass_file_contents = pg_pass_file.read()
            else:
                pg_pass_file_contents = ""
            if pg_pass_str not in pg_pass_file_contents:
                if (len(pg_pass_file_contents) > 0 and
                        pg_pass_file_contents[-1] != "\n"):
                    pg_pass_str = f"\n{pg_pass_str}"
                pg_pass_file.write(pg_pass_str)

        # pgpass file is only read when permissions are set to 0600
        pg_file_path.chmod(0o600)
