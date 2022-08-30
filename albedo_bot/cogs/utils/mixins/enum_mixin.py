
from datetime import datetime
from enum import Enum
from enum import IntEnum as BaseIntEnum


class EnumMixin:
    """
    A wrapper around an Enum that provides several helper methods
    """
    name: str

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
        Return a string representation of the enum that consists of 
            the enum name
        """
        return f"{self._name_}"


class IntEnum(EnumMixin, BaseIntEnum):
    """
    A wrapper around EnumMixin that type hints value as a int
    """
    value: int


class StrEnum(EnumMixin, Enum):
    """
    A wrapper around EnumMixin that type hints value as a str
    """
    value: str


class DatetimeEnum(EnumMixin, Enum):
    """
    A wrapper around EnumMixin that type hints value as a datetime
    """
    value: datetime
