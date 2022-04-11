from typing import Optional

from aiohttp import ClientSession, ClientResponse


class Net:
    def __init__(self):
        self.session = ClientSession()

    async def request_url(self, url: str, method: Optional[str] = 'GET', **kwargs) -> ClientResponse:
        r = await self.session.request(method, url, **kwargs)
        return r

    async def close(self):
        """
        You should always close it before session close.
        """
        await self.session.close()

    async def __aexit__(self):
        await self.close()
