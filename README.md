[![Python versions](https://img.shields.io/badge/python-3.7%2C%203.8%2C%203.9%2C%203.10-green.svg)]()
[![PyPI version](https://badge.fury.io/py/async-reduce.svg)](https://pypi.org/project/async-reduce/)


About Async-Reduce
==================

``async_reduce(coroutine)`` allows aggregate all *similar simultaneous*
ready to run `coroutine`s and reduce to running **only one** `coroutine`.
Other aggregated `coroutine`s will get result from single `coroutine`.

It can boost application performance in highly competitive execution of the
similar asynchronous operations and reduce load for inner systems.


Quick example
-------------

```python
from async_reduce import async_reduce


async def fetch_user_data(user_id: int) -> dict:
    """" Get user data from inner service """
    url = 'http://inner-service/user/{}'.format(user_id)

    return await http.get(url, timeout=10).json()


@web_server.router('/users/(\d+)')
async def handler_user_detail(request, user_id: int):
    """ Handler for get detail information about user """

    # all simultaneous requests of fetching user data for `user_id` will
    # reduced to single request
    user_data = await async_reduce(
        fetch_user_data(user_id)
    )

    # sometimes ``async_reduce`` cannot detect similar coroutines and
    # you should provide special argument `ident` for manually determination
    user_statistics = await async_reduce(
        DataBase.query('user_statistics').where(id=user_id).fetch_one(),
        ident='db_user_statistics:{}'.format(user_id)
    )

    return Response(...)
```

In that example without using ``async_reduce`` if client performs **N**
simultaneous requests like `GET http://web_server/users/42` *web_server*
performs **N** requests to *inner-service* and **N** queries to *database*.
In total: **N** simultaneous requests emits **2 * N** requests to inner systems.

With ``async_reduce`` if client performs **N** simultaneous requests *web_server*
performs **one** request to *inner-service* and **one** query to *database*.
In total: **N** simultaneous requests emit only **2** requests to inner systems.

See other real [examples](https://github.com/sirkonst/async-reduce/tree/master/examples).


Similar coroutines determination
--------------------------------

``async_reduce(coroutine)`` tries to detect similar coroutines by hashing
local variables bounded on call. It does not work correctly if:

* one of the arguments is not hashable
* coroutine function is a method of class with specific state (like ORM)
* coroutine function has closure to unhashable variable

You can disable auto-determination by setting custom key to argument ``ident``.


Use as decorator
----------------

Also library provide special decorator ``@async_reduceable()``, example:

```python
from async_reduce import async_reduceable


@async_reduceable()
async def fetch_user_data(user_id: int) -> dict:
    """" Get user data from inner service """
    url = 'http://inner-servicce/user/{}'.format(user_id)

    return await http.get(url, timeout=10).json()


@web_server.router('/users/(\d+)')
async def handler_user_detail(request, user_id: int):
    """ Handler for get detail information about user """
    return await fetch_user_data(user_id)
```


Hooks
-----

Library supports hooks. Add-on hooks:

* **DebugHooks** - print about all triggered hooks
* **StatisticsOverallHooks** - general statistics on the use of `async_reduce`
* **StatisticsDetailHooks** - like `StatisticsOverallHooks` but detail statistics
about all `coroutine` processed by `async_reduce`

Example:

```python
from async_reduce import AsyncReducer
from async_reduce.hooks import DebugHooks

# define custom async_reduce with hooks
async_reduce = AsyncReducer(hooks=DebugHooks())


async def handler_user_detail(request, user_id: int):
    user_data = await async_reduce(fetch_user_data(user_id))
```

See more detail example in [examples/example_hooks.py](https://github.com/sirkonst/async-reduce/blob/master/examples/example_hooks.py).

You can write custom hooks via inherit from [BaseHooks](https://github.com/sirkonst/async-reduce/blob/master/async_reduce/hooks/base.py).


Caveats
-------

* If single `coroutine` raises exceptions all aggregated `coroutine`s will get
same exception too

* If single `coroutine` is stuck all aggregated `coroutine`s will stuck too.
Limit execution time for `coroutine` and add retries (optional) to avoid it.

* Be careful when return mutable value from `coroutine` because single value
will shared. Prefer to use non-mutable value as coroutine return.


Development
-----------

See [DEVELOPMENT.md](https://github.com/sirkonst/async-reduce/blob/master/DEVELOPMENT.md).
