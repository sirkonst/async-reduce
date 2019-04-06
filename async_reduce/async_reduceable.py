from functools import wraps
from typing import Callable, TypeVar

from async_reduce import async_reduce, AsyncReducer

T_AsyncFunc = TypeVar('T_AsyncFunc')


def async_reduceable(
    reducer: AsyncReducer = async_reduce
) -> Callable[[T_AsyncFunc], T_AsyncFunc]:
    """
    Decorator to apply ``async_reduce(...)`` automatically for each coroutine
    function call.

    Example:

        # simple usage
        @async_reduceable()
        async def foo(arg):
            pass

        # with custom reducer class
        @async_reduceable(MyAsyncReducer)
        async def bar(arg):
            pass
    """

    def wrapper(fn):

        @wraps(fn)
        async def wrap(*args, **kwargs):
            return await reducer(fn(*args, **kwargs))

        return wrap

    return wrapper

# ---
#
# @async_reduceable()
# async def foo(arg1: int) -> str:
#     return 'foo'
#
# reveal_type(foo)
#
#
# async def amain() -> None:
#     f = foo(2)
#     reveal_type(f)
#
#     a = await f
#     reveal_type(a)
