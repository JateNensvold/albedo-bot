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


class MemberConverter(Converter):
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
            if len(ctx.message.mentions) > 0:
                member = ctx.message.mentions[0]
                assert isinstance(member, Member)
                return member
            else:
                argument = int(argument)
                member = await ctx.guild.fetch_member(argument)
                return member

        except AssertionError as exception:
            raise BadArgument(
                f"Invalid player mention `{argument}`") from exception
        except Exception as exception:
            raise BadArgument(
                f"Invalid member name or id `{argument}`") from exception


class HeroConverter(Converter):
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
        print(argument)
        try:
            try:
                int_argument = int(argument)
                hero_instance_object = GV.session.query(Hero).filter_by(
                    id=int_argument).first()
            except ValueError as exception:
                hero_instance_objects = GV.session.query(Hero).filter(
                    Hero.name.ilike(f"{argument}%")).all()
                if len(hero_instance_objects) == 1:
                    hero_instance_object = hero_instance_objects[0]
                elif len(hero_instance_objects) == 0:
                    hero_instance_object = None
                else:
                    raise BadArgument(
                        f"Invalid hero name `{argument}` too  many `Hero` "
                        f"matches ({hero_instance_objects})") from exception
            if hero_instance_object is None:
                raise AssertionError
            return hero_instance_object
        except AssertionError as exception:
            raise BadArgument(
                f"Invalid hero name or id `{argument}`") from exception
