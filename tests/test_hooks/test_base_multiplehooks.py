from asyncio import CancelledError
from collections import Counter
from typing import Any, Coroutine, Union

import pytest

from async_reduce.hooks.base import BaseHooks, MultipleHooks


def test_base_and_base():
    hook_1 = BaseHooks()
    hook_2 = BaseHooks()
    hooks = hook_1 & hook_2

    assert isinstance(hooks, MultipleHooks)
    assert len(hooks) == 2
    assert hooks.hooks_list == [hook_1, hook_2]


def test_multiple_and_base():
    hook_1 = BaseHooks()
    hooks = MultipleHooks() & hook_1

    assert isinstance(hooks, MultipleHooks)
    assert len(hooks) == 1
    assert hooks.hooks_list == [hook_1]


def test_base_and_multiple():
    hook_1 = BaseHooks()
    hooks = hook_1 & MultipleHooks()

    assert isinstance(hooks, MultipleHooks)
    assert len(hooks) == 1
    assert hooks.hooks_list == [hook_1]


def test_multiple_and_multiple():
    m_1 = MultipleHooks()
    m_2 = MultipleHooks()
    hooks = m_1 & m_2

    assert isinstance(hooks, MultipleHooks)
    assert len(hooks) == 0
    assert hooks.hooks_list == []
    assert hooks is m_1


@pytest.mark.parametrize('count', [1, 2, 255])
def test_multiple_init(count):
    hooks_list = []
    for _ in range(count):
        hooks_list.append(BaseHooks())

    hooks = MultipleHooks(*hooks_list)

    assert len(hooks) == count
    assert hooks.hooks_list == hooks_list


class CounterHooks(BaseHooks):

    def __init__(self):
        self.calls_counter = Counter()

    def on_apply_for(self, coro: Coroutine, ident: str) -> None:
        self.calls_counter['on_apply_for'] += 1

    def on_executing_for(self, coro: Coroutine, ident: str) -> None:
        self.calls_counter['on_executing_for'] += 1

    def on_reducing_for(self, coro: Coroutine, ident: str) -> None:
        self.calls_counter['on_reducing_for'] += 1

    def on_result_for(
        self, coro: Coroutine, ident: str, result: Any
    ) -> None:
        self.calls_counter['on_result_for'] += 1

    def on_exception_for(
        self, coro: Coroutine, ident: str,
        exception: Union[Exception, CancelledError]
    ) -> None:
        self.calls_counter['on_exception_for'] += 1


@pytest.mark.parametrize('count', [0, 1, 2, 255])
def test_multiple_hooks(count):
    hooks_list = []
    for _ in range(count):
        hooks_list.append(CounterHooks())

    hooks = MultipleHooks(*hooks_list)

    async def foo():
        pass

    coro = foo()

    hooks.on_apply_for(coro, 'ident')
    hooks.on_executing_for(coro, 'ident')
    hooks.on_reducing_for(coro, 'ident')
    hooks.on_result_for(coro, 'ident', None)
    hooks.on_exception_for(coro, 'ident', RuntimeError('test'))

    coro.close()

    for hook in hooks_list:
        assert hook.calls_counter['on_apply_for'] == 1
        assert hook.calls_counter['on_executing_for'] == 1
        assert hook.calls_counter['on_reducing_for'] == 1
        assert hook.calls_counter['on_result_for'] == 1
        assert hook.calls_counter['on_exception_for'] == 1
