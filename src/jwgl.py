import base64
from datetime import datetime
from typing import Optional, Union, AnyStr, Dict

from aiohttp import ClientResponse
from bs4 import BeautifulSoup

from .basicNet import Net
from .config import JWGL_LOGIN_TO_XK_URL, JWGL_KB_URL
from .exception import ProxyError
from .typing import Lesson_Dict, Schedule_Dict
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
                                                   method='POST',
                                                   data=data,
                                                   headers=headers)
        resp = (await r.read()).decode()
        if resp.find("???????????????????????????"):
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

    @login_required
    async def get_class_scheduler(self,
                                  time: Optional[Union[datetime, str]] = None,
                                  time_mode: Optional[str] = '9475847A3F3033D1E05377B5030AA94D') \
            -> Dict[int, Schedule_Dict]:
        """
        time should be like "2022-02-02",
        time_mode now can only be "9475847A3F3033D1E05377B5030AA94D"
        """
        if time is None:
            time = str(datetime.now().strftime("%Y-%m-%d"))
        else:
            if isinstance(time, datetime):
                time = str(time.strftime("%Y-%m-%d"))

        data = {
            "rq": time,
            "sjmsValue": time_mode
        }
        r = await self.request_url(JWGL_KB_URL, method="POST", data=data)
        resp = await r.read()
        return JWGL_PARSER.scheduler(resp)


class JWGL_PARSER:

    @staticmethod
    def scheduler(html: AnyStr) -> Dict[int, Schedule_Dict]:
        soup = BeautifulSoup(html, "lxml")
        # print(soup)
        data = {}
        # Weekdays
        weekdays = soup.find("tr")
        for idx in range(1, len(ths := weekdays.find_all('th'))):
            if "??????" in ths[idx].text:
                data[idx] = Schedule_Dict({"weekday": ths[idx].text,
                                           "lessons": []})

        # Lessons
        no_schedule_lessons = soup.find("div").text.split(":")[-1]
        data[0] = Schedule_Dict({"weekday": 0,
                                 "lessons": [name for name in no_schedule_lessons.split(",")[:-1]]})
        lesson_attr_dict = {
            "????????????": "score",
            "????????????": "type",
            "????????????": "name",
            "????????????": "detail_time",
            "????????????": 'place',
            "?????????": "sort"
        }

        trs = weekdays.find_all_next("tr")
        for row in trs:
            crs_idx = row.find_next("td")
            text = crs_idx.get_text(separator='|', strip=True).split("|")
            lesson_idx = text[0]
            lesson_time = text[-1]

            for i in range(1, 8):
                crs_idx = crs_idx.find_next("td")
                p = crs_idx.find('p')
                if p is None:
                    lesson_dict = {
                        k: ""
                        for k in lesson_attr_dict.values()
                    }
                else:
                    lesson_dict = {}
                    texts = p.get('title', "").split('<br/>')
                    for k in texts:
                        if "???" in k:
                            k = k.split("???")
                            lesson_dict[lesson_attr_dict[k[0]]] = k[1]
                lesson_dict['time'] = lesson_time
                lesson_dict['lesson_index'] = lesson_idx
                data[i]['lessons'].append(Lesson_Dict(lesson_dict))
        return data
