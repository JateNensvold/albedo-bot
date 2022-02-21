from discord.ext import commands
from sqlalchemy.orm import Session
from albedo_bot.database.database import Database

bot = commands.Bot(command_prefix="-")
user = "postgres"
password = "postgres"
address = "172.20.0.7"
database_name = "afk_database"

DATABASE = Database(user, password, address, database_name)
session = Session(bind=DATABASE.engine, autoflush=True, autocommit=True)

# def get_prefix():
#     """[summary]
#     """

#     bot.get_prefix()