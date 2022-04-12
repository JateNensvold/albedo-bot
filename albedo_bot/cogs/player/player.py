from discord.ext import commands
from discord import Role, Member
from albedo_bot.cogs.utils.converters.member_converter import MemberConverter
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from albedo_bot.bot import AlbedoBot


class Player(commands.Cog):
    """_summary_

    Args:
        commands (_type_): _description_
    """

    def __init__(self, bot: "AlbedoBot"):
        """_summary_

        Args:
            bot (AlbedoBot): _description_
        """
        self.bot = bot

    @bot.group()
    async def player(self, ctx: commands.Context):
        """[summary]

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        """
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid sub command passed...')

    async def register_player(self, ctx: commands.Context, discord_member: Member,
                              guild_role: Role):
        """[summary]

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        """

        guild_result = GV.session.query(Guild).filter_by(
            discord_id=guild_role.id).first()

        if guild_result is None:
            await ctx.send(
                f"'{guild_role.name}' is not a registered guild, ensure it is a "
                "registered guild before adding a player to it")
            return

        player_result = GV.session.query(Player).filter_by(
            discord_id=discord_member.id).first()

        if player_result is not None:
            guild_object = GV.session.query(Guild).filter_by(
                discord_id=player_result.guild_id).first()
            if guild_object is None:
                await ctx.send(
                    f"'{discord_member.name}' is registered with guild that no "
                    f"longer exists '{player_result.guild_id}'")
            else:
                await ctx.send(
                    f"'{discord_member.name}' is already registered with guild "
                    f"'{guild_object.name}'")
            return

        new_player = Player(discord_id=discord_member.id,
                            name=discord_member.name, guild_id=guild_role.id)
        GV.session.add(new_player)
        await ctx.send(
            f"'{discord_member.name}' registered with '{guild_result.name}'")

    async def delete_player(self, ctx: commands.Context, author: Member):
        """[summary]

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            player_id (int): [description]
        """
        player_object = GV.session.query(Player).filter_by(
            discord_id=author.id).first()
        if player_object is None:
            await ctx.send(f"Player '{author.name}' was not registered")
            return
        GV.session.delete(player_object)
        guild_object = GV.session.query(Guild).filter_by(
            discord_id=player_object.guild_id).first()
        await ctx.send(f"Player '{author.name}' was removed from guild "
                       f"{guild_object}")

    @admin.group(name="player")
    async def player_command(self, ctx: commands.Context):
        """[summary]

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        """
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid sub command passed...')

    @player_command.command(name="delete", aliases=["remove"])
    @has_permission("manager")
    async def delete(self, ctx: commands.Context, guild_member: MemberConverter):
        """[summary]

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        """
        await delete_player(ctx, guild_member)

    @player_command.command(name="add", aliases=["register"])
    @has_permission("manager")
    async def add(self, ctx: commands.Context,  guild_member: MemberConverter, guild_role: Role):
        """[summary]

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        """
        await register_player(ctx, guild_member, guild_role)
