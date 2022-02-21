import sqlalchemy

from albedo_bot.schema import base


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
        self.engine: sqlalchemy.engine.Engine = None

        self.base = base.Base
        self.metadata: sqlalchemy.MetaData = self.base.metadata

        self.postgres_connect(user, password, address, database_name)
        # if database_name is not None:
        #     self.select_database(database_name)

    def postgres_connect(self, user: str, password: str, address: str, database_name):
        """[summary]

        Args:
            user (str): [description]
            password (str): [description]
            address (str): [description]
            database_name ([type]): [description]
        """
        db_string = (f"postgresql+psycopg2://{user}:{password}@{address}/"
                     f"{database_name}")

        self.engine = sqlalchemy.create_engine(db_string)  # connect to server
        # self.connection = psycopg2.connect(
        #     database=database_name, user='postgres',
        #     password='postgres', host='127.0.0.1', port='5432'
        # )
        # self.connection.autocommit = True
        # self.cursor = self.connection.cursor()

    def create_database(self, database_name: str):
        """[summary]

        Args:
            database_name (str): [description]
        """
        if database_name not in self.list_database():
            with self.engine.connect() as connection:
                connection.execute("commit")
                connection.execute(f"CREATE DATABASE {database_name}")

        self.select_database(database_name)

    def select_database(self, database_name: str):
        """[summary]

        Args:
            database_name (str): [description]
        """
        self.postgres_connect(self.user, self.password,
                              self.address, database_name)

    def create_tables(self):
        """[summary]
        """

        self.base.metadata.create_all(self.engine)

    def list_database(self):
        """[summary]
        """
        database_tuples = self.engine.execute(
            'SELECT datname FROM pg_database;').fetchall()
        database_list = [db_string[0] for db_string in database_tuples]
        print(database_list)
        return database_list

    def list_tables(self):
        """[summary]
        """
        inspector = sqlalchemy.inspect(self.engine)
        tables = inspector.get_table_names()
        # tables = self.engine.execute(
        #     "SELECT * FROM pg_catalog.pg_tables;").fetchall()
        # # print([db_string[0] for db_string in tables])
        print(tables)
        return tables
