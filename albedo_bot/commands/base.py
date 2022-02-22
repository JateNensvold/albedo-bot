from discord.ext import commands
from sqlalchemy.orm import Session

import albedo_bot.global_values as GV
bot = commands.Bot(command_prefix="-")

session = Session(bind=GV.DATABASE.engine, autoflush=True, autocommit=True)

# def get_prefix():
#     """[summary]
#     """

#     bot.get_prefix()
