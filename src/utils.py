from typing import TypeVar, Callable, Coroutine, Union

from .exception import LoginRequireException

T = TypeVar("T", bound=Union[Callable, Coroutine])


def login_required(func: T):
    def wrapper(cls, *args, **kwargs) -> T:
        if hasattr(cls, '_is_login'):
            if cls._is_login:
                return func(cls, *args, **kwargs)
        raise LoginRequireException('You need to login first!')

    return wrapper
