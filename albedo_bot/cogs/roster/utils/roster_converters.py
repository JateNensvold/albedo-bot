from typing import Union
from discord.ext import commands


class HeroConverter(commands.Converter):
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
        print(argument)
        try:
            print(ctx.bot)
            try:
                int_argument = int(argument)
                hero_instance_object = GV.session.query(Hero).filter_by(
                    id=int_argument).first()
            except ValueError as exception:
                hero_instance_objects = GV.session.query(Hero).filter(
                    Hero.name.ilike(f"{argument}%")).all()
                if len(hero_instance_objects) == 1:
                    hero_instance_object = hero_instance_objects[0]
                elif len(hero_instance_objects) == 0 and argument in GV.HERO_ALIAS:
                    hero_database_name = GV.HERO_ALIAS[argument]
                    hero_instance_object = GV.session.query(Hero).filter_by(
                        name=hero_database_name).first()
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
