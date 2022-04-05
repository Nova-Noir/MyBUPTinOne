import base64
from typing import Optional

from aiohttp import ClientResponse

from .basicNet import Net
from .config import JWGL_LOGIN_TO_XK_URL
from .exception import ProxyError
from .utils import login_required
from .webvpn import WebVPN


class JWGL(Net):
    def __init__(self,
                 username: str,
                 password: str,
                 proxy: Optional[bool] = False,
                 proxy_username: Optional[str] = None,
                 proxy_password: Optional[str] = None):
        super().__init__()
        self.username = username
        self.password = password
        self._is_login = False
        self.cookie = None
        self.proxy = None

        if proxy:
            if proxy_username is None:
                proxy_username = username
            if proxy_password is None:
                proxy_password = password
            self.proxy = WebVPN(proxy_username, proxy_password)
            self.request_url = self.proxy.request_webvpn_url

    async def login(self, **kwargs) -> bool:
        data = {
            "userAccount": self.username,
            "userPassword": "",
            "encoded": JWGL.encodeInp(self.username) + "%%%" + JWGL.encodeInp(self.password)
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        if self.proxy is not None:
            await self.close()
            status, proxy_data = await self.proxy.login(**kwargs)
            if not status:
                raise ProxyError("Proxy error!\nError Msg: %s" % str(proxy_data))
            self.session = self.proxy.session
        r: ClientResponse = await self.request_url(JWGL_LOGIN_TO_XK_URL,
                                                   'https',
                                                   method='POST',
                                                   data=data,
                                                   headers=headers)
        resp = (await r.read()).decode()
        if resp.find("教学一体化服务平台"):
            if not self.proxy:
                self.cookie = r.cookies
            self._is_login = True
            return True

    @staticmethod
    def encodeInp(text: str) -> str:
        return base64.b64encode(text.encode()).decode()

    @login_required
    @property
    async def cookies(self):
        if self.proxy is not None:
            return self.proxy.cookies
        return self.cookie
