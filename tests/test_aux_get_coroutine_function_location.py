import asyncio

import pytest

from async_reduce.aux import get_coroutine_function_location


async def coro_function():
    pass


@asyncio.coroutine
def gen_function():
    pass


async def test_coro():
    coro = coro_function()

    result = get_coroutine_function_location(coro)
    assert result == (
        'tests.test_aux_get_coroutine_function_location:coro_function'
    )

    coro.close()


async def test_gen():
    coro = gen_function()

    result = get_coroutine_function_location(coro)
    assert result == (
        'asyncio.coroutines:gen_function'
    )

    coro.close()


@pytest.mark.parametrize('value', [
    [], [''], ['/other/']
])
async def test_unmatched_with_sys_path(monkeypatch, value):
    monkeypatch.setattr('async_reduce.aux._cached_sys_path', [])

    coro = coro_function()

    result = get_coroutine_function_location(coro)
    assert result == '~:coro_function'

    coro.close()
