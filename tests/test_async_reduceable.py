import asyncio

import pytest
from asynctest import CoroutineMock

from async_reduce import async_reduceable
from async_reduce.async_reducer import AsyncReducer

pytestmark = pytest.mark.asyncio


async def test_decorator_default():
    mock = CoroutineMock()

    @async_reduceable()
    async def foo(arg, *, kw):
        """My foo doc"""
        await mock(arg, kw=kw)

        return 'result {} {}'.format(arg, kw)

    assert foo.__name__ == 'foo'
    assert foo.__doc__ == 'My foo doc'

    coros = [
        foo('arg', kw='kw'),
        foo('arg', kw='kw')
    ]
    results = await asyncio.gather(*coros)

    mock.assert_awaited_once_with('arg', kw='kw')
    assert all(res == 'result arg kw' for res in results)


async def test_decorator_with_arg():
    mock = CoroutineMock()

    reducer = AsyncReducer()

    @async_reduceable(reducer)
    async def foo(arg, *, kw):
        """My foo doc"""
        await mock(arg, kw=kw)

        return 'result {} {}'.format(arg, kw)

    assert foo.__name__ == 'foo'
    assert foo.__doc__ == 'My foo doc'

    coros = [
        foo('arg', kw='kw'),
        foo('arg', kw='kw')
    ]
    results = await asyncio.gather(*coros)

    mock.assert_awaited_once_with('arg', kw='kw')
    assert all(r == 'result arg kw' for r in results)
