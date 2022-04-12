from typing import Union
from discord.ext.commands import Converter, Context, BadArgument
from discord import Role, Member
from discord.utils import get
import albedo_bot.global_values as GV
from albedo_bot.schema.hero import Hero


class GuildConverter(Converter):
    """_summary_

    Args:
        Converter (_type_): _description_
    """

    async def convert(self, ctx: Context, argument: Union[str, int]):
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
                guild_role = get(ctx.guild.roles, id=argument)
                return guild_role
        except AssertionError as exception:
            raise BadArgument(
                f"Invalid guild mention `{argument}`") from exception
        except Exception as exception:
            raise BadArgument(
                f"Invalid guild name or id `{argument}`") from exception
