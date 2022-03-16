import asyncio
import inspect
import typing  # noqa
from functools import partial
from typing import Coroutine, Tuple, Any, TypeVar, Awaitable, Optional

from async_reduce.aux import get_coroutine_function_location
from async_reduce.hooks.base import BaseHooks

T_Result = TypeVar('T_Result')


class AsyncReducer:

    def __init__(self, hooks: Optional[BaseHooks] = None) -> None:
        self._running = {}  # type: typing.Dict[str, asyncio.Future]
        self._hooks = hooks

    def __call__(
        self,
        coro: Coroutine[Any, Any, T_Result],
        *,
        ident: Optional[str] = None
    ) -> Awaitable[T_Result]:
        # assert inspect.getcoroutinestate(coro) == inspect.CORO_CREATED

        if not ident:
            ident = self._auto_ident(coro)

        if self._hooks:
            self._hooks.on_apply_for(coro, ident)

        future, created = self._get_or_create_future(ident)

        if created:
            self._running[ident] = future
            coro_runner = self._runner(ident, coro, future)

            if self._hooks:
                self._hooks.on_executing_for(coro, ident)

            asyncio.create_task(coro_runner)
        else:
            if self._hooks:
                self._hooks.on_reducing_for(coro, ident)

            coro.close()
            del coro

        return self._waiter(future)

    @staticmethod
    def _auto_ident(coro: Coroutine[Any, Any, T_Result]) -> str:
        func_loc = get_coroutine_function_location(coro)

        try:
            hsh = hash(tuple(
                inspect.getcoroutinelocals(coro).items()
            ))
        except TypeError:
            raise TypeError(
                'Unable to auto calculate identity for coroutine because using'
                ' unhashable arguments, you should set `ident` manual like:'
                '\n\tawait async_reduce({}(...), ident="YOU-IDENT-FOR-THAT")'
                ''.format(getattr(coro, '__name__'))
            )

        return '{}(<state_hash:{}>)'.format(func_loc, hsh)

    def _get_or_create_future(self, ident: str) -> Tuple[asyncio.Future, bool]:
        f = self._running.get(ident, None)
        if f is not None:
            return f, False
        else:
            f = asyncio.Future()
            self._running[ident] = f
            return f, True

    async def _runner(
        self,
        ident: str,
        coro: Coroutine[Any, Any, T_Result],
        future: asyncio.Future
    ) -> None:
        try:
            result = await coro
        except (Exception, asyncio.CancelledError) as e:
            future.set_exception(e)

            if self._hooks:
                self._hooks.on_exception_for(coro, ident, e)
        else:
            future.set_result(result)

            if self._hooks:
                self._hooks.on_result_for(coro, ident, result)
        finally:
            del self._running[ident]

    @classmethod
    async def _waiter(cls, future: asyncio.Future) -> T_Result:
        wait_future = asyncio.Future()  # type: asyncio.Future

        future.add_done_callback(partial(
            cls._set_wait_future_result, wait_future=wait_future
        ))

        return await wait_future

    @staticmethod
    def _set_wait_future_result(
        result_future: asyncio.Future, wait_future: asyncio.Future
    ) -> None:
        try:
            wait_future.set_result(result_future.result())
        except (Exception, asyncio.CancelledError) as e:
            wait_future.set_exception(e)


async_reduce = AsyncReducer()

# ---
#
# reveal_type(async_reduce)
#
# async def fetch(url: str) -> str:
#     print(url)
#     return url
#
#
# async def amain() -> None:
#     f = async_reduce(fetch('a'))
#     reveal_type(f)
#
#     a = await f
#     reveal_type(a)
