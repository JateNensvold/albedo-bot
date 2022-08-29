
import functools
from typing import TYPE_CHECKING, Any, Generic, List, TypeVar, Union

from sqlalchemy import select
from sqlalchemy.sql.expression import Select
from sqlalchemy.engine.result import ChunkedIteratorResult
from sqlalchemy.ext.asyncio import AsyncSession

from albedo_bot.utils.message.message_send import EmbedWrapper
from albedo_bot.utils.errors import DatabaseSessionError

if TYPE_CHECKING:
    from albedo_bot.bot import AlbedoBot

S = TypeVar("S")


class SelectWrapper(Generic[S]):
    """_summary_

    Args:
        Generic (_type_): _description_
    """

    def __init__(self, *schema: S):
        """_summary_

        Args:
            schema (S): _description_
        """
        self.select: Select = select(*schema)

    def where(self, *args):
        """_summary_
        """
        self.select = self.select.where(*args)
        return self

    def join(self, *args):
        """_summary_
        """
        self.select = self.select.join(*args)
        return self

    def order_by(self, *args):
        """_summary_

        Returns:
            _type_: _description_
        """
        self.select = self.select.order_by(*args)
        return self


def db_select(*schema: S) -> SelectWrapper[S]:
    """
    Create a SelectWrapper that wraps the select statement created from
        sqlalchemy.select, this allows for type checking/hinting to be kept
        intact when  running select/execution on Database/Schema Objects

    Args:
        schema (S): Object/Schema type being selected on

    Returns:
        S: SelectWrapper around select statement
    """

    return SelectWrapper(*schema)


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


class ScalarWrapper(Generic[S]):
    """
    Wrapper around the execution results 
    """

    def __init__(self, session: AsyncSession, select_object: SelectWrapper[S]):
        """
        Initialize the ScalarWrapper with a database session and the selection 
            object the database with

        Args:
            select_wrapper (SelectWrapper[S]): _description_

        Returns:
            _type_: _description_
        """
        self.session = session
        self.select_object = select_object
        self.execution_result: ChunkedIteratorResult = None
        self.executed = False

    async def _execute(self):
        """
        Fetch the data using the selection_object
        """
        if not self.executed:
            self.execution_result: ChunkedIteratorResult = (
                await self.session.execute(self.select_object.select))
            self.executed = True

    @_execution_decorator()
    async def all(self) -> List[S]:
        """
        Get a list of all the objects returned from the selection results

        Returns:
            List[S]: a list of objects
        """
        return self.execution_result.scalars().all()

    @_execution_decorator()
    async def all_objects(self) -> List[S]:
        """
        Get a list of all the scalars/rows that were returned from the
            selection results

        Returns:
            List[S]: a list of scalars/rows
        """
        return self.execution_result.all()

    @_execution_decorator()
    async def first(self) -> Union[S, None]:
        """
        Return the first result that was returned from the selection results

        Returns:
            S: Result object when result is found, None otherwise
        """
        return self.execution_result.scalars().first()

    @_execution_decorator()
    async def raw(self) -> Union[S, None]:
        """
        Return the raw scalar results

        Returns:
            S: raw result object from selection execution
        """
        return self.execution_result


def db_execute(session: AsyncSession,
               select_object: SelectWrapper[S]) -> ScalarWrapper[S]:
    """
    Create a ScalarWrapper that wraps the execution result of a
        'selectWrapper', this allows for type checking/hinting to be kept
        intact when  running select/execution on Database/Schema Objects

    Args:
        select_object (SelectWrapper[S]): SelectionResult to wrap

    Returns:
        ScalarWrapper[S]: ScalarWrapper around 'SelectWrapper' result
    """

    return ScalarWrapper(session, select_object)


class DatabaseMixin:
    """
    A mixin that implements several commands to interact with a database
    through sessions. The object that that inherits from this class must set
    self.bot to an instance of `AlbedoBot` or self.session to an 
    `AsyncSession` with the database
    """

    bot: "AlbedoBot"

    _session: AsyncSession

    @property
    def session(self):
        """
        Return an AsyncSession object if one can be found

        Returns:
            AsyncSession: a session object connect to the database
        """
        if hasattr(self, "bot"):
            return self.bot.session
        else:
            return self._session

    @session.setter
    def session(self, new_session: AsyncSession):
        """
        Sets _session to a new AsyncSession

        Args:
            new_session (AsyncSession): new AsyncSession
        """
        self._session = new_session

    def db_select(self, *schema: S) -> SelectWrapper[S]:
        """
        Create a SelectWrapper that wraps the select statement created from
            sqlalchemy.select, this allows for type checking/hinting to be kept
            intact when  running select/execution on Database/Schema Objects

        Args:
            schema (S): Object/Schema type being selected on

        Returns:
            S: SelectWrapper around select statement
        """

        return SelectWrapper(*schema)

    async def db_add(self, database_object: Any):
        """
        Add/Update an Sqlalchemy object so its persisted in the database

        Args:
            database_object (Any): object getting persisted to database
        """
        # Check if the database object has a pre_commit command to run before
        #   adding to database
        pre_commit = getattr(database_object, "pre_commit", None)

        if pre_commit is not None:
            database_object.pre_commit()

        self.session.add(database_object)
        await self.session.commit()
        await self.session.refresh(database_object)

    async def db_delete(self, database_object: Any):
        """
        Delete an object from the database

        *Note, while in the same transaction after calling this function calls
            to the database may fail with the following

            ```
            MissingGreenlet: greenlet_spawn has not been called; can't call
            await_only() here. Was IO attempted in an unexpected place?
            (Background on this error at: https://sqlalche.me/e/14/xd2s)
            ```

        Args:
            database_object (Any): _description_
        """
        # Commit any changes before deleting

        try:
            await self.session.delete(database_object)

            # Commit to check if any  exceptions, errors or constraints were raised
            await self.session.commit()
        except Exception as exception:
            await self.session.rollback()
            await self.session.refresh(database_object)
            embed_wrapper = EmbedWrapper(
                description=f"Unable to delete {database_object} due to \n ```{exception}```")

            raise DatabaseSessionError(
                embed_wrapper=embed_wrapper) from exception

    async def rollback(self):
        """
        Reverse the current database transaction to erase any database actions
        that have occurred
        """
        await self.session.rollback()

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

        return ScalarWrapper(self.session, select_object)
