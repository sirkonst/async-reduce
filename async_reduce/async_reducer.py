import asyncio
from enum import Enum
import inspect
import typing  # noqa
from typing import Coroutine, Tuple, Any, TypeVar, Awaitable, Optional
import sys

from async_reduce.stats import AggregatedStats

PY_VERSION = float(sys.version_info[0]) + sys.version_info[1] / 10


T_Result = TypeVar('T_Result')


class StatsLevel(Enum):
    OVERALL = 1
    DETAILED = 2


class AsyncReducer:

    def __init__(self, stats_level: StatsLevel = None) -> None:
        self._running = {}  # type: typing.Dict[str, asyncio.Future]
        self._stats_level = stats_level
        self._stats = {}    # type: typing.Dict[Optional[str], AggregatedStats]

    def __call__(
        self,
        coro: Coroutine[Any, Any, T_Result],
        *,
        ident: Optional[str] = None
    ) -> Awaitable[T_Result]:
        # assert inspect.getcoroutinestate(coro) == inspect.CORO_CREATED

        if not ident:
            ident = self._auto_ident(coro)

        future, created = self._get_or_create_future(ident)

        if created:
            self._running[ident] = future
            coro_runner = self._runner(ident, coro, future)
            if PY_VERSION >= 3.7:
                asyncio.create_task(coro_runner)
            else:
                asyncio.ensure_future(coro_runner)
        else:
            coro.close()

        self._add_stats(ident, created)

        return self._waiter(future)

    def _add_stats(self, ident: str, created: bool):
        if not self._stats_level:
            return
        key = {
            StatsLevel.OVERALL: None,
            StatsLevel.DETAILED: ident,
        }[self._stats_level]
        stats = self._stats.setdefault(key, AggregatedStats())
        stats.consume(float(created))

    @staticmethod
    def _auto_ident(coro: Coroutine[Any, Any, T_Result]) -> str:
        name = getattr(coro, '__qualname__', getattr(coro, '__name__'))
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

        return '_auto_ident:{}:{}'.format(name, hsh)

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
        coro: Awaitable[T_Result],
        future: asyncio.Future
    ) -> None:
        try:
            result = await coro
        except Exception as e:
            future.set_exception(e)
        else:
            future.set_result(result)
        finally:
            del self._running[ident]

    @staticmethod
    async def _waiter(future: asyncio.Future) -> T_Result:
        if PY_VERSION >= 3.7:
            return await future
        else:
            await asyncio.wait_for(future, timeout=None)
            return future.result()


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
