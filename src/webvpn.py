import re
from enum import Enum
from typing import Optional, AnyStr, Tuple, Dict

from aiohttp import ClientResponse
from aiohttp.client_exceptions import ContentTypeError

from .basicNet import Net
from .config import WEBVPN_LOGIN_URL, WEBVPN_BASE_URL, WEBVPN_DO_LOGIN_URL, WEBVPN_USER_INFO_URL
from .crypto import AES_encrypt, AES
from .exception import RequestError
from .utils import login_required


class WebVPN(Net):
    def __init__(self, username: str, password: str):
        super().__init__()
        self.username = username
        self.password = password
        self._is_login = False
        self.cookie = None

    async def login(self, captcha: Optional[str] = '', captcha_id: Optional[str] = '') -> Tuple[bool, Dict]:
        headers = {
            "Host": WEBVPN_BASE_URL.split('//')[-1],
            "Referer": WEBVPN_LOGIN_URL,
            "Origin": WEBVPN_BASE_URL,
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest"
        }

        data = {
            "auth_type": "local",
            "username": self.username,
            "sms_code": '',
            "password": self.password,
            "captcha": captcha,
            "needCaptcha": 'true' if captcha else 'false',
            "captcha_id": captcha_id if captcha else ''
        }

        r = await self.request_url(WEBVPN_DO_LOGIN_URL,
                                   'POST',
                                   headers=headers,
                                   data=data,
                                   cookies=await self.cookies)
        if r.status == 200:
            resp = await r.json()
            if resp.get('success'):
                self._is_login = True
                return True, resp
            else:
                return False, resp

        raise RequestError('Failed to login! Error Code: [%s], Error Message: %s' % r.status, (await r.read()).decode())

    @login_required
    async def get_info(self) -> Dict:
        r = await self.request_url(WEBVPN_USER_INFO_URL,
                                   'GET',
                                   cookies=await self.cookies)
        return await r.json()

    async def is_alive(self) -> bool:
        r = await self.request_url(WEBVPN_USER_INFO_URL,
                                   'GET',
                                   cookies=await self.cookies)
        try:
            await r.json()
            self._is_login = True
            return True
        except ContentTypeError:
            self._is_login = False
            return False

    @staticmethod
    def encrypt_url(url: str,
                    protocol: Optional[str] = 'http',
                    wrdvpnKey: Optional[AnyStr] = 'wrdvpnisthebest!',
                    wrdvpnIV: Optional[AnyStr] = 'wrdvpnisthebest!') -> str:
        if url.startswith('https://'):
            url = url[8:]
        elif url.startswith('http://'):
            url = url[7:]
        port = ''

        if re_match := re.search(r'\[[A-Fa-f0-9:]+?]', url):
            v6 = re_match.group()
            url = url[len(v6):]
        segments = url.split('?')[0].split(':')
        if len(segments) > 1:
            port = segments[1].split('/')[0]
            url = url[:len(segments[0])] + url[len(segments[0]) + len(port) + 1:]

        if protocol != 'connection':
            idx = url.find('/')
            if idx == -1:
                url = WebVPN.encrypt(url, wrdvpnKey, wrdvpnIV)
            else:
                host = url[:idx]
                path = url[idx:]
                url = WebVPN.encrypt(host, wrdvpnKey, wrdvpnIV) + path
        if port:
            url = "/" + protocol + "-" + port + "/" + url
        else:
            url = "/" + protocol + "/" + url

        return WEBVPN_BASE_URL + url

    @staticmethod
    def encrypt(text: AnyStr, key: AnyStr, iv: AnyStr) -> str:
        length = len(text)
        if isinstance(key, str):
            key = key.encode('UTF-8')
        text = WebVPN.text_right_append(text, 'utf8')
        enc = AES_encrypt(text, key, iv, AES.MODE_CFB, 'UTF-8', segment_size=16 * 8)
        return key.hex() + enc.hex()[:length * 2 if length * 2 >= len(enc) else len(enc)]

    @staticmethod
    def text_right_append(text: AnyStr, mode: str) -> AnyStr:
        segmentByteSize = 16 if mode == 'utf8' else 32
        count = segmentByteSize - len(text) % segmentByteSize
        if count == segmentByteSize:
            return text
        if isinstance(text, str):
            return text + '0' * count
        return text + b'0' * count

    @login_required
    async def request_webvpn_url(self,
                                 url: str,
                                 protocol: Optional[str] = 'http',
                                 method: Optional[str] = 'GET',
                                 **kwargs) -> ClientResponse:
        url = WebVPN.encrypt_url(url, protocol)
        r = await self.request_url(url, method, **kwargs)
        return r

    @property
    async def cookies(self):
        if self.cookie is None:
            r = await self.request_url(WEBVPN_LOGIN_URL, 'GET')
            self.cookie = r.cookies
        return self.cookie


class WebVPN_Parser:

    def __init__(self, html: AnyStr):
        self.html = html if isinstance(html, str) else html.decode()

    def get_captcha(self):
        pass


class LOGIN_ENUM(Enum):
    INVALID_ACCOUNT = 'INVALID_ACCOUNT'
    INVALID_COOKIE = 'INVALID_COOKIE'
    CAPTCHA_FAILED = 'CAPTCHA_FAILED'
