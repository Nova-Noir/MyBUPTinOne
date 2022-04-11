class RequestError(BaseException):
    pass


class LoginRequireException(BaseException):
    pass


class ProxyError(BaseException):
    pass


class QRCodeExpiredException(BaseException):
    pass
