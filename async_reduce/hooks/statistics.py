from asyncio import CancelledError
from typing import Any, Coroutine, Counter, Union

from async_reduce.aux import get_coroutine_function_location
from async_reduce.hooks.base import BaseHooks


class StatisticsOverallHooks(BaseHooks):
    """
    General statistics:

        * total - count of all ``async_reduce`` calls
        * executed - count of aggregated coroutines calls
        * reduced - count of reduced to aggregated coroutines
        * errors - count of raised errors from coroutines
    """

    def __init__(self) -> None:
        self.total = 0
        self.executed = 0
        self.reduced = 0
        self.errors = 0

    def __str__(self) -> str:
        return 'Stats(total={}, executed={}, reduced={}, errors={})'.format(
            self.total, self.executed, self.reduced, self.errors
        )

    def on_apply_for(self, coro: Coroutine[Any, Any, Any], ident: str) -> None:
        self.total += 1

    def on_result_for(
        self, coro: Coroutine[Any, Any, Any], ident: str, result: Any
    ) -> None:
        self.executed += 1

    def on_reducing_for(
        self, coro: Coroutine[Any, Any, Any], ident: str
    ) -> None:
        self.reduced += 1

    def on_exception_for(
        self, coro: Coroutine[Any, Any, Any], ident: str,
        exception: Union[Exception, CancelledError]
    ) -> None:
        self.errors += 1


class StatisticsDetailHooks(BaseHooks):

    def __init__(self) -> None:
        self.total = Counter[str]()
        self.executed = Counter[str]()
        self.reduced = Counter[str]()
        self.errors = Counter[str]()

    def __str__(self) -> str:
        return ''.join((
            'Top total:\n',
            ''.join(
                '\t{}: {}\n'.format(name, count)
                for name, count in self.total.most_common()
            ),
            'Top executed:\n',
            ''.join(
                '\t{}: {}\n'.format(name, count)
                for name, count in self.executed.most_common()
            ),
            'Top reduced:\n',
            ''.join(
                '\t{}: {}\n'.format(name, count)
                for name, count in self.reduced.most_common()
            ),
            'Top errors:\n',
            ''.join(
                '\t{}: {}\n'.format(name, count)
                for name, count in self.errors.most_common()
            )
        ))

    def on_apply_for(self, coro: Coroutine[Any, Any, Any], ident: str) -> None:
        self.total[get_coroutine_function_location(coro)] += 1

    def on_executing_for(
        self, coro: Coroutine[Any, Any, Any], ident: str
    ) -> None:
        self.executed[get_coroutine_function_location(coro)] += 1

    def on_reducing_for(
        self, coro: Coroutine[Any, Any, Any], ident: str
    ) -> None:
        self.reduced[get_coroutine_function_location(coro)] += 1

    def on_exception_for(
        self, coro: Coroutine[Any, Any, Any], ident: str,
        exception: Union[Exception, CancelledError]
    ) -> None:
        self.errors[get_coroutine_function_location(coro)] += 1
