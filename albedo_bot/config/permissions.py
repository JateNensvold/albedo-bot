
import collections
import json
from typing import Any, Dict, List, NamedTuple
from discord import Member, Role


class UserPermission(NamedTuple):
    """_summary_

    Args:
        NamedTuple (_type_): _description_
    """
    user_id: int
    name: str
    permission: int
    permission_name: str


class RolePermission(NamedTuple):
    """_summary_

    Args:
        NamedTuple (_type_): _description_
    """
    role_id: int
    name: str
    permission: int
    permission_name: str


class Permissions:
    """[summary]
    """

    def __init__(self, permission_config: Dict[str, Dict]):
        """_summary_

        self.permission_name_lookup is a dictionary that maps a "role" defined in the permission_config to an integer value that represents the required permission level associated with it
        self.role_lookup is a dictionary that maps a "discord role" to the permission level(int) associated with it
        self.user_lookup is a dictionary that maps a "discord username" to the permission level(int) associated with it

        Args:
            permission_config (Dict[str, Dict]): _description_
        """
        self.permission_name_lookup: Dict[str, int] = {}
        self.role_lookup: Dict[int, UserPermission] = {}
        self.user_lookup: Dict[int, RolePermission] = {}

        self.load_permission(permission_config)

    def lookup(self, author: Member):
        """_summary_

        Args:
            author (User): _description_
        """

        author_roles: List[Role] = author.roles

        author_id: int = author.id

        permission_level = 0

        if author_id in self.user_lookup:
            user_object = self.user_lookup[author_id]
            permission_level = user_object.permission

        for role in author_roles:
            if role.id in self.role_lookup:
                role_object = self.role_lookup[role.id]
                permission_level = max(
                    permission_level, role_object.permission)

        return permission_level

    @ classmethod
    def from_json(cls, json_path: str):
        """_summary_

        Args:
            json_path (str): _description_
        """

        with open(json_path, "r", encoding="utf-8") as config_file:
            config_data = json.load(config_file)
            permissions = Permissions(config_data)
        return permissions

    def load_permission(self, permission_config: Dict[str, Dict]):
        """
        Load permissions in permission_config into permissions lookup
            dictionaries(permission_name_lookup, role_lookup, user_lookup)

        Args:
            permission_config (Dict[str, Dict]): config dictionary loaded from
                permission config/JSON
        """
        for permission_name, permission_data in permission_config.items():
            users_with_permission: list[
                tuple[int, str]] = permission_data["users"]
            roles_with_permission: list[
                tuple[int, str]] = permission_data["roles"]
            permission_level = permission_data["priority"]
            self.permission_name_lookup[
                permission_name.lower()] = permission_level

            for user_info in users_with_permission:
                user_instance = UserPermission(user_info[0], user_info[1],
                                               permission_level, permission_name)
                self.user_lookup[user_instance.user_id] = user_instance

            for role_info in roles_with_permission:
                role_instance = RolePermission(role_info[0], role_info[1],
                                               permission_level, permission_name)
                self.role_lookup[role_instance.role_id] = role_instance

    def generate_config(self):
        """_summary_
        """
        permission_config: Dict[str, Dict[str, Any]
                                ] = collections.defaultdict()

        for role_name, permission_level in self.permission_name_lookup.items():
            permission_config[role_name]["permission"] = permission_level
            permission_config[role_name]["permission"]["users"] = []
            permission_config[role_name]["permission"]["roles"] = []

        for role_instance in self.role_lookup.values():
            permission_config[role_instance.permission_name]["users"].append(
                [role_instance.role_id, role_instance.name])

        for user_instance in self.user_lookup.values():
            permission_config[user_instance.permission_name]["users"].append(
                [user_instance.user_id, user_instance.name])

        return permission_config

    def write_permission(self, config_path: str):
        """_summary_

        Args:
            config_path (str): _description_
        """
        permission_config = self.generate_config()
        with open(config_path, "w", encoding="utf-8") as config_file:
            config_file.write(json.dumps(permission_config))

    def unload_permission(self):
        """_summary_
        """
        for role_name in list(self.permission_name_lookup.keys()):
            del self.permission_name_lookup[role_name]

        for user_id in list(self.user_lookup.keys()):
            del self.user_lookup[user_id]

        for role_id in list(self.role_lookup.keys()):
            del self.role_lookup[role_id]

    def reload_permission(self,  permission_config: Dict[str, Dict]):
        """
        Replace existing permissions config with 'permission_config'

        Args:
            permission_config (Dict[str, Dict]): config dictionary loaded from
                permission config/JSON
        """
        self.unload_permission()
        self.load_permission(permission_config)
