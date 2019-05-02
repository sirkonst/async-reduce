import sys
from typing import Coroutine, Any, IO

from async_reduce.hooks.base import BaseHooks


class DebugHooks(BaseHooks):
    """
    Print about all triggered hooks.
    """

    def __init__(self, stream: IO[str] = sys.stderr) -> None:
        self._steam = stream

    def on_apply_for(self, coro: Coroutine, ident: str) -> None:
        print(
            '[{}] apply async_reduce() for {}'.format(ident, coro),
            file=self._steam
        )

    def on_executing_for(self, coro: Coroutine, ident: str) -> None:
        print(
            '[{}] executing for {}'.format(ident, coro),
            file=self._steam
        )

    def on_reducing_for(self, coro: Coroutine, ident: str) -> None:
        print(
            '[{}] reducing for {}'.format(ident, coro),
            file=self._steam
        )

    def on_result_for(
        self, coro: Coroutine, ident: str, result: Any
    ) -> None:
        print(
            '[{}] result for {}: {}'.format(ident, coro, result),
            file=self._steam
        )

    def on_exception_for(
        self, coro: Coroutine, ident: str, exception: Exception
    ) -> None:
        print(
            '[{}] get exception for {}: {}'.format(ident, coro, exception),
            file=self._steam
        )
