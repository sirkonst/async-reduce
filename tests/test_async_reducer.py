import asyncio
from contextlib import suppress

import pytest

from async_reduce import async_reduce

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize('count', [1, 2, 5, 10, 100, 1000])
async def test_simultaneity(count):
    result = object()

    async def mock(a, b, *, c):
        mock.await_count += 1
        return result

    mock.await_count = 0

    coros_1 = [async_reduce(mock(1, 2, c=3)) for _ in range(count)]

    results = await asyncio.gather(*coros_1)

    # mock.assert_awaited_once_with(*args, **kwargs)
    assert all(res == result for res in results)

    coros_2 = [async_reduce(mock(1, 2, c=3)) for _ in range(count)]

    results = await asyncio.gather(*coros_2)

    assert mock.await_count == 2
    assert all(res == result for res in results)


class MyTestError(Exception):
    pass


@pytest.mark.parametrize(
    'count',
    [
        1,
        2,
        5,
        10,
        100,  # 1000
    ],
)
@pytest.mark.parametrize(
    'error',
    [
        MyTestError,
        Exception,
        asyncio.TimeoutError,
        asyncio.CancelledError,
    ],
)
async def test_simultaneity_raise(count, error):
    async def mock():
        mock.await_count += 1
        raise error('test error')

    mock.await_count = 0

    coros_1 = [async_reduce(mock()) for _ in range(count)]

    results = await asyncio.gather(*coros_1, return_exceptions=True)

    assert mock.await_count == 1
    for res in results:
        assert isinstance(res, error)
        if not isinstance(res, asyncio.CancelledError):
            assert str(res) == 'test error'

    coros_2 = [async_reduce(mock()) for _ in range(count)]

    results = await asyncio.gather(*coros_2, return_exceptions=True)

    assert mock.await_count == 2
    for res in results:
        assert isinstance(res, error)
        if not isinstance(res, asyncio.CancelledError):
            assert str(res) == 'test error'


@pytest.mark.parametrize(
    'value', [{}, {'a': 'b'}, object(), type('MyClass', (), {})]
)
async def test_ident(value):
    async def foo(arg):
        return 'result'

    coro = foo({})

    with pytest.raises(TypeError) as e:
        await async_reduce(coro)

    assert str(e.value) == (
        'Unable to auto calculate identity for coroutine because'
        ' using unhashable arguments, you should set `ident` manual like:'
        '\n\tawait async_reduce(foo(...), ident="YOU-IDENT-FOR-THAT")'
    )

    result = await async_reduce(coro, ident='foo_{}'.format(id(value)))
    assert result == 'result'


async def test_prevent_cancelling():
    async def foo():
        await asyncio.sleep(2)
        return 'result'

    coro_1 = async_reduce(foo())
    coro_2 = async_reduce(foo())

    with suppress(asyncio.TimeoutError):
        await asyncio.wait_for(coro_1, 1)

    result = await coro_2
    assert result == 'result'


async def test_all_waiters_cancelled(caplog):
    caplog.set_level('ERROR', logger='asyncio')

    async def foo():
        await asyncio.sleep(1)
        return 'result'

    coro_1 = async_reduce(foo())
    coro_2 = async_reduce(foo())

    gather = asyncio.gather(coro_1, coro_2)
    try:
        await asyncio.wait_for(gather, 1)
    except asyncio.TimeoutError:
        with suppress(asyncio.CancelledError):
            await gather

        # check for "asyncio.base_futures.InvalidStateError: invalid state"
        assert 'invalid state' not in caplog.text
    else:
        assert False
