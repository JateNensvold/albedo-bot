import os
from typing import Dict, List
from albedo_bot.commands.helpers.utils import send_message
from albedo_bot.schema.hero.hero import Hero
from discord.ext.commands.context import Context
from discord.ext import commands
from discord import Emoji

from albedo_bot.commands.helpers.permissions import has_permission
from albedo_bot.global_values import bot
import albedo_bot.global_values as GV

@commands.group()
@bot.group(name="private")
@has_permission("owner")
async def private(ctx: Context):
    """
    Group of commands for all tasks that require some higher level of permissions.
    All commands require either' guild manager', 'manager' or 'admin' and higher to run

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
    """
    if ctx.invoked_subcommand is None:
        await ctx.send('Private: Invalid sub command passed...')


@private.group(name="emoji")
async def emoji(ctx: Context):
    """
    Group of commands for all tasks that require some higher level of permissions.
    All commands require either' guild manager', 'manager' or 'admin' and higher to run

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
    """
    if ctx.invoked_subcommand is None:
        await ctx.send('Emoji: Invalid sub command passed...')


@private.group(name="hero")
async def hero(ctx: Context):
    """
    Group of commands for all tasks that require some higher level of permissions.
    All commands require either' guild manager', 'manager' or 'admin' and higher to run

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
    """
    if ctx.invoked_subcommand is None:
        await ctx.send('Hero: Invalid sub command passed...')


@hero.group(name="upload")
async def upload_hero(ctx: Context, start_hero_index: int, end_hero_index: int):
    """_summary_

    Args:
        ctx (Context): _description_
        start_hero_index (int): _description_
        end_hero_index (int): _description_
    """

    hero_objects: List[Hero] = GV.session.query(Hero).all()

    emoji_list: List[Emoji] = ctx.guild.emojis
    emoji_dict: Dict[str, Emoji] = {}
    for emoji_instance in emoji_list:
        emoji_dict[emoji_instance.name] = emoji_instance

    created_emoji: List[str] = []
    if start_hero_index >= len(hero_objects):
        await send_message(
            ctx,
            f"start_hero_index must be less than {len(hero_objects)}", css=False)
        return
    for hero_instance in hero_objects[start_hero_index:end_hero_index]:
        image_path = hero_instance.hero_portrait
        image_basename = os.path.basename(image_path)
        image_name, _image_ext = os.path.splitext(image_basename)
        if image_name not in emoji_dict:
            with open(image_path, "rb") as f:
                await ctx.guild.create_custom_emoji(name=image_name, image=f.read())
                created_emoji.append(image_name)

    emoji_list: List[Emoji] = ctx.guild.emojis
    emoji_dict: Dict[str, Emoji] = {}
    for emoji_instance in emoji_list:
        emoji_dict[emoji_instance.name] = emoji_instance

    emoji_list: List[Emoji] = [emoji_dict[emoji_name]
                               for emoji_name in created_emoji]

    await send_message(ctx, _list_emoji(emoji_list), css=False)


def _list_emoji(emoji_list: List[Emoji]):
    """_summary_

    Args:
        emoji_list (List[Emoji]): _description_

    Returns:
        _type_: _description_
    """
    emoji_str_list = [
        f"{str(emoji_instance)} `{str(emoji_instance)}`" for emoji_instance in emoji_list]
    return "\n".join(emoji_str_list)


@emoji.group(name="list")
async def list_emoji(ctx: Context):
    """_summary_

    Args:
        ctx (Context): _description_
    """

    emoji_list: List[Emoji] = ctx.guild.emojis
    await send_message(ctx, _list_emoji(emoji_list), css=False)


@hero.group(name="list")
async def list_datbase_heroes(ctx: Context):
    """_summary_

    Args:
        ctx (Context): _description_
    """

    hero_objects: List[Hero] = GV.session.query(Hero).all()

    hero_str = [hero.full_repr() for hero in hero_objects]
    await send_message(ctx, "\n".join(hero_str))

commands.AutoShardedBot

class Admin(commands.Cog):
    """Admin-only commands that make the bot dynamic."""

    def __init__(self, bot_instance: commands.Bot):
        self.bot = bot_instance
        self._last_result = None
        self.sessions = set()

    @private.command(hidden=True)
    async def load(self, ctx, *, module):
        """Loads a module."""
        try:
            self.bot.load_extension(module)
        except commands.ExtensionError as e:
            await ctx.send(f'{e.__class__.__name__}: {e}')
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @private.command(hidden=True)
    async def unload(self, ctx, *, module):
        """Unloads a module."""
        try:
            self.bot.unload_extension(module)
        except commands.ExtensionError as e:
            await ctx.send(f'{e.__class__.__name__}: {e}')
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @private.group(name='reload', hidden=True, invoke_without_command=True)
    async def _reload(self, ctx, *, module):
        """Reloads a module."""
        try:
            self.bot.reload_extension(module)
        except commands.ExtensionError as e:
            await ctx.send(f'{e.__class__.__name__}: {e}')
        else:
            await ctx.send('\N{OK HAND SIGN}')


def setup(bot: commands.bot.Bot):
    bot.add_cog(Admin(bot))
