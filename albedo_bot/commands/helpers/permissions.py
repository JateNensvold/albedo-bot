from typing import Dict, List, Tuple, Callable
from discord.ext.commands.context import Context

PERMISSIONS_LOOKUP: Dict[int, "Permissions"] = {}
ROLE_LOOKUP: Dict[str, "Permissions"] = {}


class Role:
    """[summary]
    """

    def __init__(self, role_id: int, name: str):
        """[summary]

        Args:
            role_id (int): [description]
            name (str): [description]
        """
        self.name = name
        self.role_id = role_id


class User:
    """[summary]
    """

    def __init__(self, user_id: int, name: str):
        """[summary]

        Args:
            user_id (int): [description]
            name (str): [description]
        """
        self.name = name
        self.user_id = user_id


class Permissions:
    """[summary]
    """

    def __init__(self, name: str, usernames: List[Tuple[int, str]],
                 roles: List[Tuple[int, str]], priority: int):
        """[summary]

        Args:
            name (str): [description]
            usernames (List[Tuple[int, str]]): [description]
            roles (List[Tuple[int, str]]): [description]
            priority (int): [description]
        """

        self.name = name
        self.usernames = []
        self.roles = []
        self.priority = priority
        ROLE_LOOKUP[self.name] = self

        for user_id, username in usernames:
            self.usernames.append(User(user_id, username))
            PERMISSIONS_LOOKUP[user_id] = self
        for role_id, role_name in roles:
            self.roles.append(Role(role_id, role_name))
            PERMISSIONS_LOOKUP[role_id] = self


def has_permission(expected_permission: int):
    """
    A decorator factory for discord.py event hooks that have a 'Context' as
    their first argument. It checks if the person calling a command has the
    needed level of permissions to run a command. 
    """
    def permission_decorator(decorated: Callable):
        """
        Inner function of decorator used to pass decorated function to
        decorator helper

        Args:
            decorated (function): function being decorated
        """
        def _has_permission(ctx: Context, *args, **kwargs):
            """
            Decorator helper that performs permissions checks and accepts the
            parameters that will get passed to the decorated function

            Args:
                ctx (Context): invocation context containing information on how
                    a discord event/command was invoked
            """

            permission = 0

            if ctx.author.id in PERMISSIONS_LOOKUP:
                permission = max(permission, PERMISSIONS_LOOKUP[ctx.author.id])

            for role in ctx.author.roles:
                if role.id in PERMISSIONS_LOOKUP:
                    permission = max(permission, PERMISSIONS_LOOKUP[role])

            if permission >= expected_permission:
                return decorated(ctx, *args, **kwargs)
            else:
                ctx.send(
                    f"{ctx.author.name} does not have permission to use this "
                    "command, contact an admin for more details")

        return _has_permission
    return permission_decorator