from enum import Enum


class EnumMixin(Enum):
    """_summary_
    """

    @classmethod
    def list(cls):
        """_summary_

        Returns:
            _type_: _description_
        """
        return list(map(lambda c: c.value, cls))
