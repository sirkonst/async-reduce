import asyncio
import statistics
from copy import copy

import pytest
from asynctest import CoroutineMock

from async_reduce import AsyncReducer
from async_reduce.async_reducer import StatsLevel
from async_reduce.stats import AggregatedStats


@pytest.fixture()
def data_init():
    return list(range(5))


@pytest.fixture()
def data_consume():
    return list(range(5, 10))


def is_close(a, b, rtol=1e-5, atol=1e-8):
    return abs(a - b) <= atol + rtol*abs(b)


@pytest.mark.parametrize(
    'prop,ref', [
        ('n', len),
        ('std', statistics.stdev),
        ('min', min),
        ('max', max),
        ('mean', statistics.mean),
        ('pvariance', statistics.pvariance),
        ('variance', statistics.variance),
        ('std', statistics.stdev),
        ('pstd', statistics.pstdev),
    ]
)
def test_stats(
    data_init, data_consume,
    prop, ref,
):
    stats = AggregatedStats(data_init)

    data = copy(data_init)
    for datum in data_consume:
        data.append(datum)
        stats.consume(datum)
        assert is_close(getattr(stats, prop), ref(data))


async def test_reducer_stats_none():
    result = object()
    mock = CoroutineMock(return_value=result)
    async_reduce = AsyncReducer(stats_level=None)

    count = 10
    args = (1, 2)
    kwargs = {'1': 2}

    coros = [
        async_reduce(mock(*args, **kwargs))
        for _ in range(count)
    ]

    await asyncio.wait(coros)
    assert not async_reduce._stats


async def test_reducer_stats_overall():
    # inspect.getcoroutinelocals does not work for CoroutineMock
    async def coro(a, b, c):
        pass

    async_reduce = AsyncReducer(stats_level=StatsLevel.OVERALL)

    count = 10
    args_kwargs = [
        ((1, 2), {'c': 2}),
        ((3, 4), {'c': 6}),
    ]
    for args, kwargs in args_kwargs:
        coros = [
            async_reduce(coro(*args, **kwargs))
            for _ in range(count)
        ]
        await asyncio.wait(coros)

    assert len(async_reduce._stats) == 1
    assert async_reduce._stats[None].n == 20
    assert async_reduce._stats[None].mean == 9/10


async def test_reducer_stats_detailed():
    # inspect.getcoroutinelocals does not work for CoroutineMock
    async def coro(a, b, c):
        pass

    async_reduce = AsyncReducer(stats_level=StatsLevel.DETAILED)

    count = 10
    args_kwargs = [
        ((1, 2), {'c': 2}),
        ((3, 4), {'c': 6}),
    ]
    for args, kwargs in args_kwargs:
        coros = [
            async_reduce(coro(*args, **kwargs))
            for _ in range(count)
        ]
        await asyncio.wait(coros)

    assert len(async_reduce._stats) == 2
    for stats in async_reduce._stats.values():
        assert stats.n == 10
        assert stats.mean == 9 / 10
