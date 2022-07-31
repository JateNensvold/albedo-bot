
from enum import Enum


class EnumMixin(Enum):
    """_summary_
    """

    @classmethod
    def v_list(cls):
        """
        return a list of the Enum values

        Returns:
            _type_: _description_
        """
        return list(map(lambda c: c.value, cls))

    @classmethod
    def list(cls):
        """
        return a list of the Enums in the class

        Returns:
            _type_: _description_
        """
        return list(map(lambda c: c, cls))

    @classmethod
    def tuple_list(cls):
        """
        returns all the enum (name, value) as a list of tuples
        """
        return list(map(lambda c: (c.name, c.value), cls))

    def __str__(self):
        """
        """
        return f"{self._name_}"
