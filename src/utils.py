from typing import TypeVar, Callable, Coroutine, Union
from datetime import datetime

from .exception import LoginRequireException, QRCodeExpiredException

T = TypeVar("T", bound=Union[Callable, Coroutine])


def login_required(func: T):
    def wrapper(cls, *args, **kwargs) -> T:
        if hasattr(cls, '_is_login'):
            if cls._is_login:
                return func(cls, *args, **kwargs)
        raise LoginRequireException('You need to login first!')

    return wrapper


def on_qrcode_login(func: T):
    def wrapper(cls, *args, **kwargs) -> T:
        if hasattr(cls, 'qrcode_expire_time'):
            if cls.qrcode_expire_time > datetime.now().timestamp():
                return func(cls, *args, **kwargs)
        raise QRCodeExpiredException("QRCode has expired or invalid.")
    return wrapper
