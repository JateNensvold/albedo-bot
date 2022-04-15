from typing import Union

import discord
from discord.ext import commands
from discord import Role

class GuildConverter(commands.Converter):
    """_summary_

    Args:
        Converter (_type_): _description_
    """

    async def convert(self, ctx:commands.Context, argument: Union[str, int]):
        """_summary_

        Args:
            ctx (Context): _description_
            argument (Union[str, int]): _description_

        Raises:
            BadArgument: _description_

        Returns:
            _type_: _description_
        """
        try:
            if len(ctx.message.role_mentions) > 0:
                role = ctx.message.role_mentions[0]
                assert isinstance(role, Role)
                return role
            else:
                argument = int(argument)
                guild_role = discord.utils.get(ctx.guild.roles, id=argument)
                return guild_role
        except AssertionError as exception:
            raise commands.BadArgument(
                f"Invalid guild mention `{argument}`") from exception
        except Exception as exception:
            raise commands.BadArgument(
                f"Invalid guild name or id `{argument}`") from exception
