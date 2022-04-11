from datetime import datetime
from typing import Union, Tuple

from .basicNet import Net
from .config import (KTP_WECHAT_QRCODE_URL,
                     KTP_CHECK_WECHAT_LOGIN_URL,
                     KTP_LOGIN_URL,
                     KTP_FIGURE_CODE_URL,
                     KTP_SEND_CODE_URL,
                     KTP_LOGIN_PHONE_URL)
from .utils import on_qrcode_login, login_required


class KETANGPAI(Net):

    def __init__(self):
        super().__init__()
        self.qrcode_expire_time = -1
        self.qrcode_url = ''
        self.qrcode_key = ''

        self.session_id = ''
        self.figure_url = ''

        self._token = ''
        self._uid = ''
        self._is_login = False

    async def get_qrcode(self) -> bool:
        timestamp, post_ts = KETANGPAI.gen_timestamp()
        data = {
            "reqtimestamp": post_ts,
            "secondDomain": ""
        }
        r = await self.request_url(KTP_WECHAT_QRCODE_URL, 'POST', data=data)
        if r.status == 200:
            if (resp := await r.json()).get('status'):
                data = resp['data']
                self.qrcode_expire_time = timestamp + data['time']
                self.qrcode_url = data['url']
                self.qrcode_key = data['code_key']
                return True
            return False
        raise ConnectionError

    @on_qrcode_login
    async def check_wechat_login_status(self) -> bool:
        timestamp, post_ts = KETANGPAI.gen_timestamp()
        data = {
            "code_key": self.qrcode_key,
            "reqtimestamp": post_ts,
            "secondDomain": ""
        }
        r = await self.request_url(KTP_CHECK_WECHAT_LOGIN_URL, 'POST', data=data)
        if r.status == 200:
            if (resp := await r.json()).get("status"):
                self.qrcode_expire_time = -1
                self._token = resp['data']['token']
                self._uid = resp['data']['uid']
                self._is_login = True
                return True
            return False
        raise ConnectionError(r.status)

    async def login(self, account: str, password: str) -> Tuple[bool, str]:
        _, post_ts = KETANGPAI.gen_timestamp()
        data = {
            "email": account,
            "password": password,
            "remember": "1",
            "code": "",
            "mobile": "",
            "type": "login",
            "reqtimestamp": post_ts
        }
        r = await self.request_url(KTP_LOGIN_URL, 'POST', data=data)
        if r.status == 200:
            if (resp := await r.json()).get('status'):
                self._token = resp['data']['token']
                self._uid = resp['data']['uid']
                self._is_login = True
                return True, resp['message']
            return False, resp['message']
        raise ConnectionError

    async def get_figure_code(self) -> bool:
        _, post_ts = KETANGPAI.gen_timestamp()
        data = {
            "reqtimestamp": post_ts
        }
        r = await self.request_url(KTP_FIGURE_CODE_URL, 'POST', data=data)
        if r.status == 200:
            if (resp := await r.json()).get('status'):
                self.figure_url = resp['data']['url']
                self.session_id = resp['data']['sessionid']
                return True
            return False
        raise ConnectionError

    async def send_code(self, mobile: str, verify: str) -> Tuple[bool, str]:
        _, post_ts = KETANGPAI.gen_timestamp()
        data = {
            "reqtimestamp": post_ts,
            "mobile": mobile,
            "secondDomain": "",
            "sessionid": self.session_id,
            "type": "login",
            "verify": verify
        }
        r = await self.request_url(KTP_SEND_CODE_URL, 'POST', data=data)
        if r.status == 200:
            print(await r.json())
            if (resp := await r.json()).get('status'):
                return True, resp['message']
            return False, resp['message']
        raise ConnectionError

    async def login_by_phone(self, mobile: str, code: str) -> Tuple[bool, str]:
        _, post_ts = KETANGPAI.gen_timestamp()
        data = {
            "reqtimestamp": post_ts,
            "email": "",
            "password": "",
            "remember": "1",
            "code": code,
            "mobile": mobile,
            "type": "login"
        }
        r = await self.request_url(KTP_LOGIN_PHONE_URL, 'POST', data=data)
        if r.status == 200:
            if (resp := await r.json()).get('status'):
                self._token = resp['data']['token']
                self._uid = resp['data']['uid']
                self._is_login = True
                return True, resp['message']
            return False, resp['message']
        raise ConnectionError

    @staticmethod
    def gen_timestamp() -> Tuple[float, int]:
        return (timestamp := datetime.now().timestamp()), int(timestamp * 1000)


