

from discord.ext import commands
from discord import Role, Member

from albedo_bot.database.schema import Player, Guild
from albedo_bot.cogs.utils.base_cog import BaseCog
from albedo_bot.utils.message import EmbedField, send_embed
from albedo_bot.utils.errors import CogCommandError


class BasePlayerCog(BaseCog):
    """_summary_

    Args:
        commands (_type_): _description_
    """

    async def register_player(self, ctx: commands.Context,
                              discord_member: Member, guild_role: Role):
        """[summary]

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
        """
        guild_select = self.select(Guild).where(
            Guild.discord_id == guild_role.id)
        guild_result = await self.execute(guild_select).first()

        if guild_result is None:
            embed_field = EmbedField(
                "Player Error",
                f"{guild_role.mention} is not a registered guild, ensure it "
                "is a registered guild before adding a player to it")
            raise CogCommandError(embed_field_list=[embed_field])

        player_select = self.select(Player).where(
            Player.discord_id == discord_member.id)
        player_result = await self.execute(player_select).first()

        if player_result is not None:
            guild_select = self.select(Guild).where(
                Guild.discord_id == player_result.guild_id)

            guild_object = await self.execute(guild_select).first()
            if guild_object is None:
                embed_field = EmbedField(
                    "Player Error",
                    f"{discord_member.mention} is registered with guild that no"
                    f" longer exists {player_result.guild_id}")
                raise CogCommandError(embed_field_list=[embed_field])
            else:
                embed_field = EmbedField(
                    "Player Already Registered",
                    (f"{discord_member.mention} is already registered with "
                     f"guild {guild_object}"))
                raise CogCommandError(embed_field_list=[embed_field])

        new_player = Player(discord_id=discord_member.id,
                            name=discord_member.name, guild_id=guild_role.id)
        self.bot.session.add(new_player)
        embed_field = EmbedField(
            "Success",
            (f"{discord_member.mention} registered with "
             f"{guild_result}"))
        await send_embed(ctx, embed_field_list=[embed_field])

    async def delete_player(self, ctx: commands.Context, author: Member):
        """[summary]

        Args:
            ctx (Context): invocation context containing information on how
                a discord event/command was invoked
            player_id (int): [description]
        """
        select_player = self.select(Player).where(
            Player.discord_id == author.id)
        player_object = await self.execute(select_player).first()
        if player_object is None:
            embed_field = EmbedField(
                "Player Error",
                f"Player {author.mention} is not registered")
            raise CogCommandError(embed_field_list=[embed_field])

        await self.bot.session.delete(player_object)

        select_guild = self.select(Guild).where(
            Guild.discord_id == player_object.guild_id)
        guild_object = await self.execute(select_guild).first()

        embed_field = EmbedField(
            "Success",
            (f"Player {author.mention} was removed from guild "
             f"{guild_object.guild_mention_no_ping}"))
        await send_embed(ctx, embed_field_list=[embed_field])

    async def list_players(self):
        """_summary_

        Args:
            ctx (commands.Context): _description_
        """

        players_select = self.select(Player)

        players_result = await self.execute(players_select).all()
        return players_result
