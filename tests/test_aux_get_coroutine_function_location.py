import importlib
import sys

import pytest

from async_reduce.aux import get_coroutine_function_location

pytestmark = pytest.mark.asyncio


def teardown_module(module):
    """
    Reload ``async_reduce.aux`` for reset module caches after tests
    """
    from async_reduce import aux

    importlib.reload(aux)


async def coro_function():
    pass


async def test_coro():
    coro = coro_function()

    result = get_coroutine_function_location(coro)
    assert result == (
        'tests.test_aux_get_coroutine_function_location:coro_function'
    )

    coro.close()


@pytest.mark.skipif(
    sys.version_info >= (3, 10), reason='asyncio.coroutine has been removed'
)
async def test_gen():
    import asyncio

    @asyncio.coroutine
    def gen_function():
        pass

    coro = gen_function()

    result = get_coroutine_function_location(coro)
    assert result == ('asyncio.coroutines:test_gen.<locals>.gen_function')

    coro.close()


@pytest.mark.parametrize('value', [[], [''], ['/'], ['/other/']])
async def test_unmatched_with_sys_path(monkeypatch, value):
    monkeypatch.setattr('sys.path', value)

    from async_reduce import aux

    importlib.reload(aux)

    coro = coro_function()

    result = aux.get_coroutine_function_location(coro)
    assert result == '<unknown module>:coro_function'

    coro.close()
