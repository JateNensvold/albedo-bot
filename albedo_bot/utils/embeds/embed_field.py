
from typing import NamedTuple


class EmbedField(NamedTuple("EmbedField", [("name", str),
                                           ("value", str)])):
    """
    A utility class that encapsulates a lot of the information needed for a
    discord.py EmbedField
    """

    # __init__ method provided as a function stub for type hinting calls to
    #   __new__ construction
    # pylint: disable=super-init-not-called
    def __init__(self, name: str = None, value: str = None):
        """
        Set name and value for `Discord embed_field`

        Args:
            name (str, optional): _description_. Defaults to None.
            value (str, optional): _description_. Defaults to None.
        """

    def __new__(cls, name: str = None, value: str = None) -> "EmbedField":
        """
        Create a new EmbedField allowing for name and value to be set to `None`

        Args:
            name (str, optional): Name/title of the EmbedField object.
                 Defaults to None.
            value (str, optional): Description for the EmbedField object.
                 Defaults to None.

        Returns:
            EmbedField: a new EmbedField with name/value set
        """

        return super().__new__(cls, name, value)
