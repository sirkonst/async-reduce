import asyncio
import sys
from io import StringIO
import re

import pytest

from async_reduce import AsyncReducer
from async_reduce.hooks import DebugHooks

pytestmark = pytest.mark.asyncio


async def test_debug_hooks():
    stream = StringIO()

    async def foo(arg):
        return arg

    async def foo_error():
        raise RuntimeError('test')

    async_reduce = AsyncReducer(hooks=DebugHooks(stream))

    coros = [
        async_reduce(foo(1)),
        async_reduce(foo(1)),
        async_reduce(foo(2)),
        async_reduce(foo_error()),
    ]

    await asyncio.gather(*coros, return_exceptions=True)

    lines = stream.getvalue().splitlines()
    assert len(lines) == 11

    module_loc = 'tests.test_hooks.test_debug'

    assert re.fullmatch(
        r'\[{module_loc}:{func_name}\(<state_hash:-?\d+>\)\]'
        r' apply async_reduce\(\) for'
        r' <coroutine object {func_name} at 0x\w+>'
        r''.format(module_loc=module_loc, func_name=foo.__qualname__),
        lines[0]
    ) is not None, lines[0]
    assert re.fullmatch(
        r'\[{module_loc}:{func_name}\(<state_hash:-?\d+>\)\]'
        r' executing for'
        r' <coroutine object {func_name} at 0x\w+>'
        r''.format(module_loc=module_loc, func_name=foo.__qualname__),
        lines[1]
    ) is not None, lines[1]
    assert re.fullmatch(
        r'\[{module_loc}:{func_name}\(<state_hash:-?\d+>\)\]'
        r' apply async_reduce\(\) for'
        r' <coroutine object {func_name} at 0x\w+>'
        r''.format(module_loc=module_loc, func_name=foo.__qualname__),
        lines[2]
    ) is not None, lines[2]
    assert re.fullmatch(
        r'\[{module_loc}:{func_name}\(<state_hash:-?\d+>\)\]'
        r' reducing for'
        r' <coroutine object {func_name} at 0x\w+>'
        r''.format(module_loc=module_loc, func_name=foo.__qualname__),
        lines[3]
    ) is not None, lines[3]
    assert re.fullmatch(
        r'\[{module_loc}:{func_name}\(<state_hash:-?\d+>\)\]'
        r' apply async_reduce\(\) for'
        r' <coroutine object {func_name} at 0x\w+>'
        r''.format(module_loc=module_loc, func_name=foo.__qualname__),
        lines[4]
    ) is not None, lines[4]
    assert re.fullmatch(
        r'\[{module_loc}:{func_name}\(<state_hash:-?\d+>\)\]'
        r' executing for'
        r' <coroutine object {func_name} at 0x\w+>'
        r''.format(module_loc=module_loc, func_name=foo.__qualname__),
        lines[5]
    ) is not None, lines[5]
    assert re.fullmatch(
        r'\[{module_loc}:{func_name}\(<state_hash:-?\d+>\)\]'
        r' apply async_reduce\(\) for'
        r' <coroutine object {func_name} at 0x\w+>'
        r''.format(module_loc=module_loc, func_name=foo_error.__qualname__),
        lines[6]
    ) is not None, lines[6]
    assert re.fullmatch(
        r'\[{module_loc}:{func_name}\(<state_hash:-?\d+>\)\]'
        r' executing for'
        r' <coroutine object {func_name} at 0x\w+>'
        r''.format(module_loc=module_loc, func_name=foo_error.__qualname__),
        lines[7]
    ) is not None, lines[7]
    assert re.fullmatch(
        r'\[{module_loc}:{func_name}\(<state_hash:-?\d+>\)\]'
        r' result for'
        r' <coroutine object {func_name} at 0x\w+>: 1'
        r''.format(module_loc=module_loc, func_name=foo.__qualname__),
        lines[8]
    ) is not None, lines[8]
    assert re.fullmatch(
        r'\[{module_loc}:{func_name}\(<state_hash:-?\d+>\)\]'
        r' result for'
        r' <coroutine object {func_name} at 0x\w+>: 2'
        r''.format(module_loc=module_loc, func_name=foo.__qualname__),
        lines[9]
    ) is not None, lines[9]
    assert re.fullmatch(
        r'\[{module_loc}:{func_name}\(<state_hash:-?\d+>\)\]'
        r' get exception for'
        r' <coroutine object {func_name} at 0x\w+>: test'
        r''.format(module_loc=module_loc, func_name=foo_error.__qualname__),
        lines[10]
    ) is not None, lines[10]


async def test_debug_hooks_default():

    async def foo(arg):
        return arg

    async_reduce = AsyncReducer(hooks=DebugHooks())

    coros = [
        async_reduce(foo(1)),
        async_reduce(foo(1)),
        async_reduce(foo(2)),
    ]

    await asyncio.gather(*coros)


@pytest.mark.parametrize('stream', [
    sys.stderr, sys.stdout
])
async def test_debug_hooks_stream(stream):

    async def foo(arg):
        return arg

    async_reduce = AsyncReducer(hooks=DebugHooks(stream))

    coros = [
        async_reduce(foo(1)),
        async_reduce(foo(1)),
        async_reduce(foo(2)),
    ]

    await asyncio.gather(*coros)
