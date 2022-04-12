from typing import Union
from discord.ext import commands
from discord import Member


class MemberConverter(commands.Converter):
    """_summary_

    Args:
        Converter (_type_): _description_
    """

    async def convert(self, ctx: commands.Context, argument: Union[str, int]):
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
            if len(ctx.message.mentions) > 0:
                member = ctx.message.mentions[0]
                assert isinstance(member, Member)
                return member
            else:
                argument = int(argument)
                member = await ctx.guild.fetch_member(argument)
                return member

        except AssertionError as exception:
            raise commands.BadArgument(
                f"Invalid player mention `{argument}`") from exception
        except Exception as exception:
            raise commands.BadArgument(
                f"Invalid member name or id `{argument}`") from exception
