
from typing import Any, Awaitable, Callable

import discord


FuncType = Callable[[Any], Awaitable[Any]]


class Select(discord.ui.Select):
    """
    A wrapper around discord.py `Select` object that provides defaults while
    initializing the `Select` object, also allows for a callback object to be
    passed in during object initialization so a new Select class with a
    `Callback` does not need to be created for every usage of `Select`
    """

    def __init__(self,
                 options: list[discord.SelectOption],
                 callback: FuncType = None,
                 placeholder_text: str = "Select an option",
                 max_values: int = 1,
                 min_values: int = 1):
        super().__init__(placeholder=placeholder_text,
                         max_values=max_values, min_values=min_values, options=options)
        self._callback = callback

    async def callback(self, interaction: discord.Interaction):
        return await self._callback(self, interaction)


class SelectView(discord.ui.View):
    """
    A wrapper around discord.py View object

    Args:
        discord (_type_): _description_
    """

    def __init__(self, select_items: list[Select], timeout=180):
        """_summary_

        Args:
            select_items (list[Select]): _description_
            timeout (int, optional): _description_. Defaults to 180.
        """
        super().__init__(timeout=timeout)
        for selector in select_items:
            self.add_item(selector)


class SelectOption(discord.SelectOption):
    """
    A wrapper around the discord.py `SelectOption` that will store an additional
    field called original_value that helps translate the selected values when
    a callback is called on the `Select` object
    """

    def __init__(self, *args, original_value: Any = None, **kwargs) -> None:
        self.original_value = original_value
        super().__init__(*args, **kwargs)
