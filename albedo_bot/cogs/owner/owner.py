from albedo_bot.bot import AlbedoBot

from albedo_bot.cogs.owner.utils.base_owner import BaseOwnerCog
from albedo_bot.utils.checks import check_config_permission
from albedo_bot.utils.message import EmbedField, EmbedWrapper, send_embed
from click import pass_context
from discord.ext.commands.context import Context
from discord.ext import commands
from discord import Emoji, Embed, PartialEmoji

import albedo_bot.config as config


# @commands.group()
# @bot.group(name="private")
# @check_config_permission("owner")
# async def private(ctx: Context):
#     """
#     Group of commands for all tasks that require some higher level of permissions.
#     All commands require either' guild manager', 'manager' or 'admin' and higher to run

#     Args:
#         ctx (Context): invocation context containing information on how
#             a discord event/command was invoked
#     """
#     if ctx.invoked_subcommand is None:
#         await ctx.send('Private: Invalid sub command passed...')

#     @bot.group(name="private")
#     async def ping_command(self, ctx: commands.Context):
#         """[summary]

#         Args:
#             ctx (Context): invocation context containing information on how
#                 a discord event/command was invoked
#         """
#         await ctx.send("pong")
#         # if ctx.invoked_subcommand is None:
#         #     await ctx.send('Invalid sub command passed...')


# @private.group(name="emoji")
# async def emoji(ctx: Context):
#     """
#     Group of commands for all tasks that require some higher level of permissions.
#     All commands require either' guild manager', 'manager' or 'admin' and higher to run

#     Args:
#         ctx (Context): invocation context containing information on how
#             a discord event/command was invoked
#     """
#     if ctx.invoked_subcommand is None:
#         await ctx.send('Emoji: Invalid sub command passed...')


# @private.group(name="hero")
# async def hero(ctx: Context):
#     """
#     Group of commands for all tasks that require some higher level of permissions.
#     All commands require either' guild manager', 'manager' or 'admin' and higher to run

#     Args:
#         ctx (Context): invocation context containing information on how
#             a discord event/command was invoked
#     """
#     if ctx.invoked_subcommand is None:
#         await ctx.send('Hero: Invalid sub command passed...')


# @hero.group(name="upload")
# async def upload_hero(ctx: Context, start_hero_index: int, end_hero_index: int):
#     """_summary_

#     Args:
#         ctx (Context): _description_
#         start_hero_index (int): _description_
#         end_hero_index (int): _description_
#     """

#     hero_objects: List[Hero] = GV.session.query(Hero).all()

#     emoji_list: List[Emoji] = ctx.guild.emojis
#     emoji_dict: Dict[str, Emoji] = {}
#     for emoji_instance in emoji_list:
#         emoji_dict[emoji_instance.name] = emoji_instance

#     created_emoji: List[str] = []
#     if start_hero_index >= len(hero_objects):
#         await send_message(
#             ctx,
#             f"start_hero_index must be less than {len(hero_objects)}", css=False)
#         return
#     for hero_instance in hero_objects[start_hero_index:end_hero_index]:
#         image_path = hero_instance.hero_portrait
#         image_basename = os.path.basename(image_path)
#         image_name, _image_ext = os.path.splitext(image_basename)
#         if image_name not in emoji_dict:
#             with open(image_path, "rb") as f:
#                 await ctx.guild.create_custom_emoji(name=image_name, image=f.read())
#                 created_emoji.append(image_name)

#     emoji_list: List[Emoji] = ctx.guild.emojis
#     emoji_dict: Dict[str, Emoji] = {}
#     for emoji_instance in emoji_list:
#         emoji_dict[emoji_instance.name] = emoji_instance

#     emoji_list: List[Emoji] = [emoji_dict[emoji_name]
#                                for emoji_name in created_emoji]

#     await send_message(ctx, _list_emoji(emoji_list), css=False)


# def _list_emoji(emoji_list: List[Emoji]):
#     """_summary_

#     Args:
#         emoji_list (List[Emoji]): _description_

#     Returns:
#         _type_: _description_
#     """
#     emoji_str_list = [
#         f"{str(emoji_instance)} `{str(emoji_instance)}`" for emoji_instance in emoji_list]
#     return "\n".join(emoji_str_list)


# @emoji.group(name="list")
# async def list_emoji(ctx: Context):
#     """_summary_

#     Args:
#         ctx (Context): _description_
#     """

#     emoji_list: List[Emoji] = ctx.guild.emojis
#     await send_message(ctx, _list_emoji(emoji_list), css=False)


# @hero.group(name="list")
# async def list_datbase_heroes(ctx: Context):
#     """_summary_

#     Args:
#         ctx (Context): _description_
#     """

#     hero_objects: List[Hero] = GV.session.query(Hero).all()

#     hero_str = [hero.full_repr() for hero in hero_objects]
#     await send_message(ctx, "\n".join(hero_str))


class OwnerCog(BaseOwnerCog):
    """Admin-only commands that make the bot dynamic."""

    def __init__(self, bot: "AlbedoBot", **kwargs):
        """_summary_

        Args:
            bot (AlbedoBot): _description_
        """
        super().__init__(bot, **kwargs)
        self.permissions = config.permissions

    @commands.group(name="owner")
    @check_config_permission("owner")
    async def owner(self, ctx: commands.Context):
        """[summary]

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        """
        # if ctx.invoked_subcommand is None:
        #     await ctx.send('Invalid sub command passed...')

    @owner.command(hidden=True)
    async def load(self, ctx: Context, *, module):
        """Loads a module."""
        try:
            self.bot.load_extension(module)
        except commands.ExtensionError as e:
            await ctx.send(f'{e.__class__.__name__}: {e}')
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @owner.command(hidden=True)
    async def list(self, ctx: Context):
        """
        List all loaded modules
        """

        module_list = "\n".join(
            f"`{key}`: {lib}"for key, lib in self.bot._BotBase__extensions.items())

        await send_embed(ctx, EmbedWrapper(
            title="Loaded Modules", description=module_list))

    @owner.command(hidden=True)
    async def unload(self, ctx: Context, *, module):
        """Unloads a module."""
        try:
            self.bot.unload_extension(module)
        except commands.ExtensionError as e:
            await ctx.send(f'{e.__class__.__name__}: {e}')
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @owner.command(name='reload', hidden=True, invoke_without_command=True)
    async def _reload(self, ctx: Context, *, module):
        """Reloads a module."""
        try:
            self.bot.reload_extension(module)
        except commands.ExtensionError as e:
            await ctx.send(f'{e.__class__.__name__}: {e}')
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @owner.command(name="debug_emoji")
    async def debug_emoji(self, ctx: Context, emoji: PartialEmoji):
        """
        Send Debug information about an emoji like its `Emoji ID` and `Name`

        Args:
            emoji (PartialEmoji): emoji to debug
        """

        embed_field1 = EmbedField(
            name="Id",
            value=repr(emoji.id))

        embed_field2 = EmbedField(
            name="Name",
            value=repr(emoji.name))

        await send_embed(ctx, embed_wrapper=EmbedWrapper(
            title=f"`{emoji}`", embed_fields=[embed_field1, embed_field2]))


def setup(bot: commands.bot.Bot):
    """_summary_

    Args:
        bot (commands.bot.Bot): _description_
    """
    bot.add_cog(OwnerCog(bot, require_registration=False))
