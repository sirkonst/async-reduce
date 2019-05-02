import sys
from typing import Coroutine, Any

_cached_sys_path = sorted(set(
    path for path in sys.path if path and path != '/'
))


def get_coroutine_function_location(coro: Coroutine[Any, Any, Any]) -> str:
    """
    Get relative location for coroutine function.
    """
    code = getattr(coro, 'cr_code', None)
    if not code:  # for generator base coroutine
        code = getattr(coro, 'gi_code')

    filename = code.co_filename
    file_path = next(
        (
            filename[len(path):] for path in _cached_sys_path
            if filename.startswith(path)
        ),
        None
    )
    if file_path:
        module_path = file_path.lstrip('/').rstrip('.py').replace('/', '.')
    else:
        module_path = '<unknown module>'

    return '{}:{}'.format(
        module_path, getattr(coro, '__qualname__')
    )
