import asyncio

import pytest
from asynctest import CoroutineMock

from async_reduce import async_reduce

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize('count', [
    1, 2, 5, 10, 100, 1000
])
@pytest.mark.parametrize('args', [
    (), (1,), ('1',), (1, '1'), (1, '1', None)
])
@pytest.mark.parametrize('kwargs', [
    {}, {'1': 1}, {'1': '1'}, {'1': 1, '2': '2'}, {'1': 1, '2': '2', '3': None}
])
async def test_simultaneity(count, args, kwargs):
    result = object()
    mock = CoroutineMock(return_value=result)

    coros_1 = [
        async_reduce(mock(*args, **kwargs))
        for _ in range(count)
    ]

    done_1, pending_1 = await asyncio.wait(coros_1)
    assert not pending_1
    mock.assert_awaited_once_with(*args, **kwargs)
    assert all(f.result() == result for f in done_1)

    coros_2 = [
        async_reduce(mock(*args, **kwargs))
        for _ in range(count)
    ]

    done_2, pending_2 = await asyncio.wait(coros_2)
    assert not pending_2
    mock.assert_any_await(*args, **kwargs)
    assert mock.await_count == 2
    assert all(f.result() == result for f in done_2)


class MyTestError(Exception):
    pass


@pytest.mark.parametrize('count', [
    1, 2, 5, 10, 100,  # 1000
])
@pytest.mark.parametrize('error', [
    MyTestError, Exception, asyncio.TimeoutError, asyncio.CancelledError,
])
async def test_simultaneity_raise(count, error):
    mock = CoroutineMock(side_effect=error('test error'))

    coros_1 = [
        async_reduce(mock())
        for _ in range(count)
    ]

    done_1, pending_1 = await asyncio.wait(coros_1)
    assert not pending_1
    mock.assert_awaited_once_with()

    for f in done_1:
        with pytest.raises(error) as e:
            await f

        if not isinstance(e.value, asyncio.CancelledError):
            assert str(e.value) == 'test error'

    coros_2 = [
        async_reduce(mock())
        for _ in range(count)
    ]

    done_2, pending_2 = await asyncio.wait(coros_2)
    assert not pending_2
    mock.assert_any_await()
    assert mock.await_count == 2

    for f in done_1:
        with pytest.raises(error) as e:
            await f

        if not isinstance(e.value, asyncio.CancelledError):
            assert str(e.value) == 'test error'


@pytest.mark.parametrize('value', [
    {}, {'a': 'b'}, object(), type('MyClass', (), {})
])
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

    result = await async_reduce(
        coro, ident='foo_{}'.format(id(value))
    )
    assert result == 'result'
