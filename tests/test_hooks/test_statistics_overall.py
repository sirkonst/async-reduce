import asyncio

import pytest

from async_reduce import AsyncReducer
from async_reduce.hooks import StatisticsOverallHooks

pytestmark = pytest.mark.asyncio


async def test():

    async def foo(arg):
        return arg

    async def foo_error():
        raise RuntimeError('test')

    stats = StatisticsOverallHooks()
    async_reduce = AsyncReducer(hooks=stats)

    coros = [
        async_reduce(foo(1)),
        async_reduce(foo(1)),
        async_reduce(foo(2)),
        async_reduce(foo_error()),
    ]

    await asyncio.gather(*coros, return_exceptions=True)

    assert stats.total == 4
    assert stats.executed == 2
    assert stats.reduced == 1
    assert stats.errors == 1

    assert str(stats) == 'Stats(total=4, executed=2, reduced=1, errors=1)'
