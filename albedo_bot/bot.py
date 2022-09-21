import json
import logging
import re
import sys
import time
import traceback

from collections import Counter, deque
from datetime import datetime
from typing import Callable, Deque, Dict, Iterable, List, Union
from asyncio import current_task
from albedo_bot.cogs.utils.mixins.database_mixin import DatabaseMixin
from albedo_bot.utils.errors import MessageError

import discord
from discord.ext import commands
from discord import Guild, Member, Message, Emoji
from discord.errors import DiscordException

import albedo_bot.config as config
from albedo_bot.utils.message.message_send import send_embed_exception
from albedo_bot.cogs.help.help_cog import HelpCog


initial_extensions = (
    'cogs.player.player',
    'cogs.guild.guild',
    'cogs.roster.roster',
    'cogs.owner.owner',
    'cogs.hero.hero',
    'cogs.checklist.checklist'
    # 'cogs.admin.admin',
)

default_bot_prefix = ['%']

log = logging.getLogger(__name__)


def bot_prefix_callable(bot: "AlbedoBot", ctx: commands.Context):
    """_summary_

    Args:
        bot (commands.Bot): _description_
        msg (commands.Context): _description_

    Returns:
        _type_: _description_
    """
    bot_id = bot.user.id

    prefix_list = [f'<@!{bot_id}> ', f'<@{bot_id}> ']

    # Configure guild specific prefixes here if desired...
    if ctx.guild is None:
        prefix_list.extend(default_bot_prefix)
    else:
        prefix_list.extend(bot.prefixes.get(ctx.guild.id, default_bot_prefix))

    return prefix_list


class AlbedoBot(commands.Bot, DatabaseMixin):
    """
    AlbedoBot class that runs discord a discord bot for 
        AFK Arena and discord Guild management utilities

    Args:
        commands (_type_): _description_
    """
    # Owner Id for tosh
    owner_string = "@tosh#8118"
    tosh_id = "<@270762725179654144>"

    description = ("AFK Arena Roster Management Bot Written by "
                   f"{owner_string}")

    help_description = (
        f"To get started using the bot use the command `{default_bot_prefix[0]}"
        "register`.\n To register your roster check out the roster commands "
        f"with `{default_bot_prefix[0]}help roster`.\n To view more commands "
        "check out the categories below.")

    def __init__(self, event_loop=None):
        intents = discord.Intents(
            guilds=True,
            members=True,
            bans=True,
            emojis=True,
            voice_states=True,
            messages=True,
            reactions=True,
            message_content=True,
        )
        allowed_mentions = discord.AllowedMentions(
            roles=False, everyone=False, users=True)

        self.default_prefix = default_bot_prefix[0]

        # Initialize before super call so help_command can use command_cache
        self.command_cache: dict[str,
                                 Union[commands.Command, commands.Group]] = {}

        super().__init__(command_prefix=bot_prefix_callable,
                         #  event_loop=event_loop,
                         description=self.description,
                         intents=intents,
                         allowed_mentions=allowed_mentions,
                         enable_debug_events=True,
                         help_command=HelpCog())

        self.owner_id = self.tosh_id

        self.uptime: datetime = None
        self._emoji_cache: Dict[str, Emoji] = {}
        self._prev_events: Deque[Message] = deque(maxlen=10)

        # in case of even further spam, add a cooldown mapping
        # for people who excessively spam commands
        self.spam_control = commands.CooldownMapping.from_cooldown(
            10, 12.0, commands.BucketType.user)

        # A counter to auto-ban frequent spammers
        # Triggering the rate limit 5 times in a row will auto-ban the user
        #   from the bot.
        self._auto_spam_count = Counter()
        # Cache that stores a mapping of cog names without the word "cog" in them
        self._cog_cache: dict[str, str] = {}

        self.database = config.objects.database
        self.database.postgres_connect()

        # Update the method used to scope database sessions
        self.database.update_scoped_session(self.get_current_scope)

        self.bot = self

        self.task_cache = {}

    @property
    def mention(self):
        """
        Returns a discord mention of the bot

        Returns:
            str: a discord bot mention
        """
        return f"<@!{self.user.id}>"

    @property
    def emoji_cache(self):
        """
        A dictionary that caches the bots emojis on startup so allow for quick
            fetching of emojis by name

        Returns:
            Dict[str, Emoji]: a dictionary of emojis
        """
        if len(self._emoji_cache) == 0:
            for emoji in self.emojis:
                self._emoji_cache[emoji.name] = emoji
        return self._emoji_cache

    @property
    def session(self):
        """
        Return the current database `AsyncSession`
        """
        return self.database.session

    @property
    def session_producer(self):
        """
        Return the session_producer used to create and mange scope of the
        current session
        """
        return self.database.session_producer

    @property
    def cog_cache(self):
        """
        Cache that stores a mapping of cog names without the word "cog" in them
        """

        if len(self._cog_cache) == 0:
            for cog_name, _cog_object in self.cogs.items():
                cog_name_lower = cog_name.lower()
                if "cog" in cog_name_lower:
                    new_cog_name = re.sub(r"cog",
                                          "", cog_name, flags=re.IGNORECASE)
                    self._cog_cache[new_cog_name] = cog_name
        return self._cog_cache

    def get_cog(self, name: str):
        """
        Get a cog by name

        Args:
            name (str): name of cog to get

        Returns:
            Cog: cog that matches `name`
        """

        if name in self.cog_cache:
            name = self.cog_cache.get(name)

        return super().get_cog(name)

    def add_command(self, command: Union[commands.Command, commands.Group]):
        """
        Add the ability to add commands to multiple modules

        Args:
            command (Union[commands.Command, commands.Group]): _description_
        """

        # Remove cog parameter of a command if its original kwarg specifies
        #   it to be false

        parents = [parent.name for parent in command.parents]

        parents.append(command.name)
        full_name = f"{'.'.join(parents)}"

        if full_name in self.command_cache:
            # Checks kwargs of original command because monkey patching the
            #   decorator creating commands does not work
            if command.__original_kwargs__.get(
                    "allow_duplicate") and full_name in self.command_cache:
                original_command = self.command_cache[full_name]
                # Remove previous command and replace with newest one
                for sub_command_name, sub_command in command.all_commands.items():
                    if sub_command.name not in original_command.all_commands:
                        print(("Adding subcommand to existing module "
                               f"{full_name}: {sub_command_name}"))
                        # print(sub_command, type(sub_command),
                        #   sub_command.all_commands)
                        original_command.add_command(sub_command)
                return
        else:
            self.command_cache[full_name] = (command)

        super().add_command(command)

    def get_current_scope(self):
        """_summary_

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            time (int): _description_

        Raises:
            CogCommandError: _description_

        """

        task = current_task()
        return task

    async def on_socket_raw_receive(self, msg: Message):
        """
        Called whenever a message is received from the websocket, before it's
        processed. Unlike on_socket_response this event is always dispatched
        when a message is received and the passed data is not processed in any way.

        Args:
            msg (Message): message sent to websocket
        """
        self._prev_events.append(msg)

    async def on_command_error(self, context: commands.Context, exception: Exception):
        """_summary_

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            errors (Any): _description_
        """
        try:
            if isinstance(exception, commands.NoPrivateMessage):
                await context.author.send('This command cannot be used in private messages.')
            elif isinstance(exception, commands.DisabledCommand):
                await context.author.send('Sorry. This command is disabled and cannot be used.')
            elif isinstance(exception, commands.CommandInvokeError):
                original = exception.original
                if not isinstance(original, discord.HTTPException):
                    print(f'In {context.command.qualified_name}:',
                          file=sys.stderr)
                    traceback.print_tb(original.__traceback__)
                    print(f'{original.__class__.__name__}: {original}',
                          file=sys.stderr)
                await send_embed_exception(context, exception)
            elif isinstance(exception, commands.ArgumentParsingError):
                await context.send(exception)
            else:
                traceback.print_exception(
                    type(exception), exception, exception.__traceback__)
                if isinstance(exception, MessageError) or issubclass(
                        type(exception), MessageError):
                    print(exception.embed_wrapper)

                # No traceback available so just print the exception
                await send_embed_exception(context, exception)
        # pylint: disable=broad-except
        except Exception as _exception:
            await self.bot.rollback()

    def get_guild_prefixes(self, guild, *,
                           local_inject: Callable = bot_prefix_callable):
        """
        Get the prefix that the bot should respond to for `guild`

        Args:
            guild (_type_): _description_
            local_inject (_type_, optional): function that returns prefix
                for a message.
                 Defaults to bot_prefix_callable.

        Returns:
            _type_: _description_
        """
        proxy_msg = discord.Object(id=0)
        proxy_msg.guild = guild
        return local_inject(self, proxy_msg)

    def get_raw_guild_prefixes(self, guild_id):
        """_summary_

        Args:
            guild_id (_type_): _description_

        Returns:
            _type_: _description_
        """
        return self.prefixes.get(guild_id, default_bot_prefix)

    async def set_guild_prefixes(self, guild, prefixes):
        """_summary_

        Args:
            guild (_type_): _description_
            prefixes (_type_): _description_

        Raises:
            RuntimeError: _description_
        """
        if len(prefixes) == 0:
            await self.prefixes.put(guild.id, [])
        elif len(prefixes) > 10:
            raise RuntimeError('Cannot have more than 10 custom prefixes.')
        else:
            await self.prefixes.put(guild.id, sorted(set(prefixes), reverse=True))

    async def add_to_blacklist(self, object_id: int):
        """_summary_

        Args:
            object_id (int): _description_
        """

        await self.blacklist.put(object_id, True)

    async def remove_from_blacklist(self, object_id: int):
        """_summary_

        Args:
            object_id (int): _description_
        """
        try:
            await self.blacklist.remove(object_id)
        except KeyError:
            pass

    async def query_member_named(self, guild: Guild, argument, *, cache: bool = False):
        """Queries a member by their name, name + discrim, or nickname.
        Parameters
        ------------
        guild: Guild
            The guild to query the member in.
        argument: str
            The name, nickname, or name + discrim combo to check.
        cache: bool
            Whether to cache the results of the query.
        Returns
        ---------
        Optional[Member]
            The member matching the query or None if not found.
        """
        if len(argument) > 5 and argument[-5] == '#':
            username, _, discriminator = argument.rpartition('#')
            members: List[Member] = await guild.query_members(username, limit=100, cache=cache)
            return discord.utils.get(members, name=username, discriminator=discriminator)
        else:
            members: List[Member] = await guild.query_members(argument, limit=100, cache=cache)
            return discord.utils.find(lambda m: m.name == argument or m.nick == argument, members)

    async def get_or_fetch_member(self, guild: Guild, member_id: int):
        """
        Looks up a member in cache or fetches if not found.

        Parameters
        -----------
        guild: Guild
            The guild to look in.
        member_id: int
            The member ID to search for.
        Returns
        ---------
        Optional[Member]
            The member or None if not found.
        """

        member: Member = guild.get_member(member_id)
        if member is not None:
            return member

        members: List[Member] = await guild.query_members(
            limit=1, user_ids=[member_id], cache=True)
        if not members:
            return None
        return members[0]

    async def resolve_member_ids(self, guild: Guild, member_ids: Iterable[int]):
        """Bulk resolves member IDs to member instances, if possible.
        Members that can't be resolved are discarded from the list.
        This is done lazily using an asynchronous iterator.
        Note that the order of the resolved members is not the same as the input.
        Parameters
        -----------
        guild: Guild
            The guild to resolve from.
        member_ids: Iterable[int]
            An iterable of member IDs.
        Yields
        --------
        Member
            The resolved members.
        """

        needs_resolution: List[int] = []
        for member_id in member_ids:
            member: Member = guild.get_member(member_id)
            if member is not None:
                yield member
            else:
                needs_resolution.append(member_id)

        total_need_resolution = len(needs_resolution)
        if total_need_resolution == 1:
            members: List[Member] = await guild.query_members(
                limit=1, user_ids=needs_resolution, cache=True)
            if members:
                yield members[0]
        elif total_need_resolution <= 100:
            # Only a single resolution call needed here
            resolved: List[Member] = await guild.query_members(
                limit=100, user_ids=needs_resolution, cache=True)
            for member in resolved:
                yield member
        else:
            # We need to chunk these in bits of 100...
            for index in range(0, total_need_resolution, 100):
                to_resolve = needs_resolution[index: index + 100]
                members: List[Member] = await guild.query_members(
                    limit=100, user_ids=to_resolve, cache=True)
                for member in members:
                    yield member

    async def on_ready(self):
        """_summary_
        """
        if not self.uptime:
            self.uptime: datetime = datetime.now()

        print(f'Ready: {self.user} (ID: {self.user.id}) (Time: {self.uptime})')

    def log_spammer(self, ctx: commands.Context, message: Message, retry_after: float, *,
                    autoblock: bool = False):
        """_summary_

        Args:
            ctx (_type_): _description_
            message (_type_): _description_
            retry_after (_type_): _description_
            autoblock (bool, optional): _description_. Defaults to False.

        Returns:
            _type_: _description_
        """
        guild_name = getattr(ctx.guild, 'name', 'No Guild (DMs)')
        guild_id: Union[int, None] = getattr(ctx.guild, 'id', None)
        fmt = 'User %s (ID %s) in guild %r (ID %s) spamming, retry_after: %.2fs'
        log.warning(fmt, message.author, message.author.id,
                    guild_name, guild_id, retry_after)
        if not autoblock:
            return

    async def process_commands(self, message: Message):
        ctx: commands.Context = await self.get_context(message)

        if ctx.author.id in self.blacklist:
            return

        if ctx.guild is not None and ctx.guild.id in self.blacklist:
            return

        bucket: commands.Cooldown = self.spam_control.get_bucket(message)
        current = message.created_at.timestamp()
        retry_after = bucket.update_rate_limit(current)
        author_id: int = message.author.id
        # Check if user is rate limited or getting banned
        if retry_after and author_id != self.owner_id:
            self._auto_spam_count[author_id] += 1
            if self._auto_spam_count[author_id] >= 5:
                await self.add_to_blacklist(author_id)
                del self._auto_spam_count[author_id]
                await self.log_spammer(ctx, message, retry_after,
                                       autoblock=True)
            else:
                self.log_spammer(ctx, message, retry_after)
            return
        else:
            self._auto_spam_count.pop(author_id, None)

        try:
            await self.invoke(ctx)
        finally:
            # Commit any uncommited changes to database
            try:
                await self.session_producer.commit()
            finally:
                # closes currently scoped session before disposing of it
                #   i.e.(cleans up session database resources for command
                #   currently being processed)
                await self.session_producer.remove()

    async def on_message(self, message: Message):
        """_summary_

        Args:
            message (Message): _description_
        """
        if message.author.bot:
            return
        await self.process_commands(message)

    async def on_guild_join(self, guild: Guild):
        """_summary_

        Args:
            guild (_type_): _description_
        """
        if guild.id in self.blacklist:
            await guild.leave()

    async def close(self):
        await super().close()

    async def setup_hook(self) -> None:

        # Configured prefixes for each server/guild using the bot
        self.prefixes = config.objects.prefixes

        # Users and guilds blacklisted from using bot
        self.blacklist = config.objects.blacklist

        # Permissions config to check users permissions
        self.permissions = config.objects.permissions

        for extension in initial_extensions:
            try:
                await self.load_extension(extension)
            except DiscordException as _load_failure:
                print(f"Failed to load extension {extension}", file=sys.stderr)
                traceback.print_exc()

    async def start(self):  # pylint: disable=arguments-differ
        """_summary_
        """

        # # Configured prefixes for each server/guild using the bot
        # self.prefixes = config.objects.prefixes

        # # Users and guilds blacklisted from using bot
        # self.blacklist = config.objects.blacklist

        # # Permissions config to check users permissions
        # self.permissions = config.objects.permissions

        # for extension in initial_extensions:
        #     try:
        #         await self.load_extension(extension)
        #     except DiscordException as _load_failure:
        #         print(f"Failed to load extension {extension}", file=sys.stderr)
        #         traceback.print_exc()

        await super().start(config.TOKEN, reconnect=True)
