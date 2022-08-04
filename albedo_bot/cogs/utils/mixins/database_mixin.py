
import functools
from typing import TYPE_CHECKING, Any, Generic, List, TypeVar, Union

from sqlalchemy import select
from sqlalchemy.sql.expression import Select
from sqlalchemy.engine.result import ChunkedIteratorResult


from albedo_bot.utils.message import EmbedWrapper
from albedo_bot.utils.errors import DatabaseSessionError

if TYPE_CHECKING:
    from albedo_bot.bot import AlbedoBot

S = TypeVar("S")


class SelectWrapper(Generic[S]):
    """_summary_

    Args:
        Generic (_type_): _description_
    """

    def __init__(self, schema: S):
        """_summary_

        Args:
            schema (S): _description_
        """
        self.select: Select = select(schema)

    def where(self, *args):
        """_summary_
        """
        self.select = self.select.where(*args)
        return self


def select_wrapper(schema: S) -> SelectWrapper[S]:
    """_summary_

    Args:
        schema (S): _description_

    Returns:
        SelectWrapper[S]: _description_
    """
    return SelectWrapper(schema)


class ScalarWrapper(Generic[S]):
    """
    Wrapper around the execution results 
    """

    def __init__(self, bot: "AlbedoBot", select_object: SelectWrapper[S]):
        """_summary_

        Args:
            select_wrapper (SelectWrapper[S]): _description_

        Returns:
            _type_: _description_
        """
        self.bot = bot
        self.select_object = select_object
        self.execution_result: ChunkedIteratorResult = None

    async def _execute(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        self.execution_result: ChunkedIteratorResult = (
            await self.bot.session.execute(self.select_object.select))

    def _execution_decorator():  # pylint: disable=no-method-argument
        """
        Decorator for any method that interacts with the 'execution_result'
            i.e it automatically calls _execute before that result is accessed
        """
        def wrapper(func):
            @functools.wraps(func)
            async def wrapped(self: "ScalarWrapper", *args, **kwargs):
                """
                Execute select statement before 'func' is called
                """
                await self._execute()  # pylint: disable=protected-access
                return await func(self, *args, **kwargs)
            return wrapped
        return wrapper

    @_execution_decorator()
    async def all(self) -> List[S]:
        """_summary_

        Returns:
            List[S]: _description_
        """
        return self.execution_result.scalars().all()

    @_execution_decorator()
    async def first(self) -> Union[S, None]:
        """
        Return the first result found

        Returns:
            S: Result object when result is found, None otherwise
        """
        return self.execution_result.scalars().first()


def scalar_wrapper(bot: "AlbedoBot", select_object: SelectWrapper[S]):
    """_summary_

    Args:
        bot (AlbedoBot): _description_
        select_object (SelectWrapper[S]): _description_

    Returns:
        _type_: _description_
    """
    return ScalarWrapper(bot, select_object)


class DatabaseMixin:
    """_summary_
    """

    # def __init__(self):
    bot: "AlbedoBot"

    def db_select(self, schema: S) -> SelectWrapper[S]:
        """
        Create a SelectWrapper that wraps the select statement created from
            sqlalchemy.select, this allows for type checking/hinting to be kept
            intact when  running select/execution on Database/Schema Objects

        Args:
            schema (S): Object/Schema type being selected on

        Returns:
            S: SelectWrapper around select statement
        """

        return SelectWrapper(schema)

    async def db_add(self, database_object: Any):
        """_summary_

        Args:
            database_object (Any): _description_
        """

        self.bot.session.add(database_object)
        await self.bot.session.commit()
        await self.bot.session.refresh(database_object)

    async def db_delete(self, database_object: Any):
        """
        Delete an object from the database

        *Note, while in the same transaction calls after deleting from the
            database may fail with the following

            ```
            MissingGreenlet: greenlet_spawn has not been called; can't call
            await_only() here. Was IO attempted in an unexpected place?
            (Background on this error at: https://sqlalche.me/e/14/xd2s)
            ```

        Args:
            database_object (Any): _description_
        """
        # Commit any changes before deleting
        # self.bot.session.commit()

        try:
            await self.bot.session.delete(database_object)

            # Commit to check if any  exceptions, errors or constraints were raised
            await self.bot.session.commit()
        except Exception as exception:
            await self.bot.session.rollback()
            await self.bot.session.refresh(database_object)
            embed_wrapper = EmbedWrapper(
                description=f"Unable to delete {database_object} due to \n ```{exception}```")

            raise DatabaseSessionError(embed_wrapper=embed_wrapper) from exception

    def db_execute(self, select_object: SelectWrapper[S]) -> ScalarWrapper[S]:
        """
        Create a ScalarWrapper that wraps the execution result of a
            'selectWrapper', this allows for type checking/hinting to be kept
            intact when  running select/execution on Database/Schema Objects

        Args:
            select_object (SelectWrapper[S]): SelectionResult to wrap

        Returns:
            ScalarWrapper[S]: ScalarWrapper around 'SelectWrapper' result
        """

        return ScalarWrapper(self.bot, select_object)
