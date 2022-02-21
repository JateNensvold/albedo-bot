# Import schema files so create_all creates all tables
import albedo_bot.schema  # pylint: disable=unused-import

from albedo_bot.database.database import Database


def main():
    """[summary]
    """
    user = "postgres"
    password = "postgres"
    address = "172.20.0.7"
    database_name = "afk_database"
    afk_database = Database(user, password, address)
    afk_database.create_database(database_name)
    # afk_database.select_database(database_name)
    afk_database.create_tables()
    print(afk_database.engine.url)
    afk_database.list_tables()


if __name__ == "__main__":
    main()
