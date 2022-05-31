# from typing import Union

# from discord.ext import commands

# from albedo_bot.bot import AlbedoBot
# from albedo_bot.cogs.utils.mixins.database_mixin import DatabaseMixin
# from albedo_bot.database.schema import Hero
# import albedo_bot.config as config


# class HeroConverter(commands.Converter, DatabaseMixin):
#     """_summary_

#     Args:
#         Converter (_type_): _description_
#     """
#     hero_alias = config.hero_alias

#     async def convert(self, ctx: commands.Context, argument: Union[str, int]):
#         """_summary_

#         Args:
#             ctx (Context): _description_
#             argument (Union[str, int]): _description_

#         Raises:
#             BadArgument: _description_

#         Returns:
#             _type_: _description_
#         """
#         self.bot: AlbedoBot = ctx.bot
#         try:
#             try:
#                 int_argument = int(argument)
#                 hero_instance_select = self.db_select(
#                     Hero).where(Hero.id == int_argument)
#                 hero_instance_result = await self.db_execute(hero_instance_select).first()
#             except ValueError as exception:
#                 hero_instances_select = self.db_select(
#                     Hero).where(Hero.name.ilike(f"{argument}%"))
#                 hero_instances_result = await self.db_execute(hero_instances_select).all()
#                 if len(hero_instances_result) == 1:
#                     hero_instance_result = hero_instances_result[0]
#                 elif len(hero_instances_result) == 0 and argument in self.hero_alias:
#                     hero_database_name = self.hero_alias.get(argument)
#                     hero_instance_select = self.db_select(Hero).where(
#                         Hero.name == hero_database_name)
#                     hero_instance_result = await self.db_execute(hero_instance_select).first()
#                 else:
#                     raise commands.BadArgument(
#                         f"Invalid hero name `{argument}` too  many `Hero` "
#                         f"matches ({hero_instances_result})") from exception
#             if hero_instance_result is None:
#                 raise AssertionError
#             return hero_instance_result
#         except AssertionError as exception:
#             raise commands.BadArgument(
#                 f"Invalid hero name or id `{argument}`") from exception
