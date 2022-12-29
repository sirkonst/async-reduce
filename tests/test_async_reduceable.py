import asyncio

import pytest

from async_reduce import async_reduceable
from async_reduce.async_reducer import AsyncReducer

pytestmark = pytest.mark.asyncio


async def test_decorator_default():
    @async_reduceable()
    async def foo(arg, *, kw):
        foo.await_count += 1

        return 'result {} {}'.format(arg, kw)

    foo.await_count = 0

    coros = [foo('arg', kw='kw'), foo('arg', kw='kw')]
    results = await asyncio.gather(*coros)

    assert foo.await_count == 1
    assert all(res == 'result arg kw' for res in results)


async def test_decorator_with_arg():
    async def mock():
        mock.await_count += 1

    mock.await_count = 0

    reducer = AsyncReducer()

    @async_reduceable(reducer)
    async def foo(arg, *, kw):
        """My foo doc"""
        await mock()

        return 'result {} {}'.format(arg, kw)

    assert foo.__name__ == 'foo'
    assert foo.__doc__ == 'My foo doc'

    coros = [foo('arg', kw='kw'), foo('arg', kw='kw')]
    results = await asyncio.gather(*coros)

    assert mock.await_count == 1
    assert all(r == 'result arg kw' for r in results)
