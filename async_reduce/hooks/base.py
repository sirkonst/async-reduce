from typing import Coroutine, Any


class BaseHooks:
    """
    Interface for implementation of hooks.
    """

    def on_apply_for(self, coro: Coroutine, ident: str) -> None:
        """
        Calls when ``async_reduce`` apply to coroutine.
        """

    def on_executing_for(self, coro: Coroutine, ident: str) -> None:
        """
        Calls when coroutine executing as aggregated coroutine.
        """

    def on_reducing_for(self, coro: Coroutine, ident: str) -> None:
        """
        Calls when coroutine reduced to aggregated coroutine.
        """

    def on_result_for(
        self, coro: Coroutine, ident: str, result: Any
    ) -> None:
        """
        Calls when aggregated coroutine returns value.
        """

    def on_exception_for(
        self, coro: Coroutine, ident: str, exception: Exception
    ) -> None:
        """
        Calls when aggregated coroutine raises exception.
        """

    def __and__(self, other: 'BaseHooks') -> 'MultipleHooks':
        if isinstance(other, MultipleHooks):
            return other & self

        return MultipleHooks(self, other)


class MultipleHooks(BaseHooks):
    """
    Internal class to gather multiple hooks (via operator `&`).

    Each hook will be called in the addition sequence.
    """

    def __init__(self, *hooks: BaseHooks) -> None:
        self.hooks_list = [*hooks]

    def __and__(self, other: BaseHooks) -> 'MultipleHooks':
        if isinstance(other, MultipleHooks):
            self.hooks_list.extend(other.hooks_list)
            return self

        self.hooks_list.append(other)
        return self

    def __len__(self):
        """ Count of gathered hooks """
        return len(self.hooks_list)

    def on_apply_for(self, coro: Coroutine, ident: str) -> None:
        for hooks in self.hooks_list:
            hooks.on_apply_for(coro, ident)

    def on_executing_for(self, coro: Coroutine, ident: str) -> None:
        for hooks in self.hooks_list:
            hooks.on_executing_for(coro, ident)

    def on_reducing_for(self, coro: Coroutine, ident: str) -> None:
        for hooks in self.hooks_list:
            hooks.on_reducing_for(coro, ident)

    def on_result_for(
        self, coro: Coroutine, ident: str, result: Any
    ) -> None:
        for hooks in self.hooks_list:
            hooks.on_result_for(coro, ident, result)

    def on_exception_for(
        self, coro: Coroutine, ident: str, exception: Exception
    ) -> None:
        for hooks in self.hooks_list:
            hooks.on_exception_for(coro, ident, exception)