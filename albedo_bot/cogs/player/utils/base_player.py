import traceback
from discord.ext import commands
from discord import Role, Member

from albedo_bot.database.schema import Player, Guild
from albedo_bot.cogs.utils.base_cog import BaseCog
from albedo_bot.utils.message import EmbedWrapper, send_embed
from albedo_bot.utils.errors import CogCommandError, DatabaseSessionError


class BasePlayerCog(BaseCog):
    """_summary_

    Args:
        commands (_type_): _description_
    """

    # pylint: disable=no-member
    @BaseCog.admin.group(name="player")
    async def player_admin(self, ctx: commands.Context):
        """
        A group of players commands that require elevated permissions to run

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        """

    async def register_player(self, ctx: commands.Context,
                              discord_member: Member, guild_role: Role):
        """[summary]

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        """
        guild_select = self.db_select(Guild).where(
            Guild.discord_id == guild_role.id)
        guild_result = await self.db_execute(guild_select).first()

        if guild_result is None:
            embed_wrapper = EmbedWrapper(
                title="Player Error",
                description=(
                    f"{guild_role.mention} is not a registered guild, ensure "
                    "it is a registered guild before adding a player to it"))
            raise CogCommandError(embed_wrapper=embed_wrapper)

        player_select = self.db_select(Player).where(
            Player.discord_id == discord_member.id)
        player_result = await self.db_execute(player_select).first()

        if player_result is not None:
            guild_select = self.db_select(Guild).where(
                Guild.discord_id == player_result.guild_id)

            guild_object = await self.db_execute(guild_select).first()
            if guild_object is None:
                # Should be impossible state to get into with protected deletes
                #   in self.delete
                embed_wrapper = EmbedWrapper(
                    title="Player Error",
                    description=(
                        f"{discord_member.mention} is registered with "
                        f"guild that no longer exists {player_result.guild_id}"))
                raise CogCommandError(embed_wrapper=embed_wrapper)
            else:
                embed_wrapper = EmbedWrapper(
                    title="Player Already Registered",
                    description=(
                        f"{discord_member.mention} is already registered with "
                        f"guild {guild_object}"))
                raise CogCommandError(embed_wrapper=embed_wrapper)

        new_player = Player(discord_id=discord_member.id,
                            name=discord_member.name, guild_id=guild_role.id)
        self.bot.session.add(new_player)
        bot_prefix = self.bot.default_prefix
        await send_embed(ctx, embed_wrapper=EmbedWrapper(
            description=(f"{discord_member.mention} has been successfully "
                         f"registered with {guild_result}.\n\nTo begin adding "
                         "your hero roster to the bot use the command "
                         f"`{bot_prefix}hero upload` with screenshots of your "
                         "roster from the Heroes page in-game, or checkout the "
                         f"other commands on the bot with `{bot_prefix}help`")))

    async def delete_player(self, ctx: commands.Context, player: Member):
        """
        Delete a player from a guild

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            player (Member): discord members name, mention, or user ID
        """
        select_player = self.db_select(Player).where(
            Player.discord_id == player.id)
        player_object = await self.db_execute(select_player).first()
        if player_object is None:
            embed_wrapper = EmbedWrapper(
                title="Player Error",
                description=f"Player {player.mention} is not registered")
            raise CogCommandError(embed_wrapper=embed_wrapper)

        try:
            await self.db_delete(player_object)
        except DatabaseSessionError as exception:

            embed_wrapper = exception.embed_wrapper
            embed_wrapper.description = (
                f"{embed_wrapper.description}\n\n"
                f"Try running '{self.bot.default_prefix}admin roster clear "
                f"{player}' before this command")
            raise CogCommandError(
                embed_wrapper=exception.embed_wrapper) from exception
        select_guild = self.db_select(Guild).where(
            Guild.discord_id == player_object.guild_id)
        guild_object = await self.db_execute(select_guild).first()

        await send_embed(ctx, embed_wrapper=EmbedWrapper(
            description=(f"Player {player.mention} was removed from guild "
                         f"{guild_object.guild_mention_no_ping}")))

    async def list_players(self, player_filter: str):
        """_summary_

        Args:
            ctx (commands.Context): _description_
        """

        if player_filter is None:
            players_select = self.db_select(Player)
        else:
            players_select = self.db_select(Player).where(
                Player.name.ilike(f"{player_filter}%"))

        players_result = await self.db_execute(players_select).all()
        return players_result
