import asyncio

import pytest

from async_reduce import AsyncReducer
from async_reduce.hooks import StatisticsDetailHooks

pytestmark = pytest.mark.asyncio


async def test():

    async def foo(arg):
        return arg

    async def foo_error():
        raise RuntimeError('test')

    stats = StatisticsDetailHooks()
    async_reduce = AsyncReducer(hooks=stats)

    coros = [
        async_reduce(foo(1)),
        async_reduce(foo(1)),
        async_reduce(foo(2)),
        async_reduce(foo_error()),
    ]

    await asyncio.gather(*coros, return_exceptions=True)

    assert stats.total == {
        'tests.test_hooks.test_statistics_detail:test.<locals>.foo': 3,
        'tests.test_hooks.test_statistics_detail:test.<locals>.foo_error': 1
    }
    assert stats.executed == {
        'tests.test_hooks.test_statistics_detail:test.<locals>.foo': 2,
        'tests.test_hooks.test_statistics_detail:test.<locals>.foo_error': 1
    }
    assert stats.reduced == {
        'tests.test_hooks.test_statistics_detail:test.<locals>.foo': 1
    }
    assert stats.errors == {
        'tests.test_hooks.test_statistics_detail:test.<locals>.foo_error': 1
    }

    assert str(stats) == ('''\
Top total:
\ttests.test_hooks.test_statistics_detail:test.<locals>.foo: 3
\ttests.test_hooks.test_statistics_detail:test.<locals>.foo_error: 1
Top executed:
\ttests.test_hooks.test_statistics_detail:test.<locals>.foo: 2
\ttests.test_hooks.test_statistics_detail:test.<locals>.foo_error: 1
Top reduced:
\ttests.test_hooks.test_statistics_detail:test.<locals>.foo: 1
Top errors:
\ttests.test_hooks.test_statistics_detail:test.<locals>.foo_error: 1
''')
