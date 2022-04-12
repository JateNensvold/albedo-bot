# from discord.ext.commands.context import Context
# from albedo_bot.commands.helpers.hero import (_add_hero, _remove_hero)
# from albedo_bot.commands.helpers.permissions import has_permission

# from albedo_bot.commands.admin.base import admin


# @admin.group(name="hero")
# async def hero_command(ctx: Context):
#     """[summary]

#     Args:
#         ctx (Context): invocation context containing information on how
#             a discord event/command was invoked
#     """
#     if ctx.invoked_subcommand is None:
#         await ctx.send('Invalid sub command passed...')


# @hero_command.command(name="register", aliases=["add"])
# @has_permission("guild_manager")
# async def register(ctx: Context, hero_name: str):
#     """[summary]

#     Args:
#         ctx (Context): invocation context containing information on how
#             a discord event/command was invoked
#         name (str): [description]
#     """
#     await _add_hero(ctx, hero_name)


# @hero_command.command(name="remove", aliases=["delete"])
# @has_permission("guild_manager")
# async def remove(ctx: Context, hero_name: str):
#     """[summary]

#     Args:
#         ctx (Context): invocation context containing information on how
#             a discord event/command was invoked
#         name (str): [description]
#     """
#     await _remove_hero(ctx, hero_name)
