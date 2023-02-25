import logging
import traceback
import aiohttp
from .utils import EMPTY_DATA


class _Client:
    def __init__(self) -> None:
        self._session:aiohttp.ClientSession = None  # type: ignore
        self.proxy = None

    async def get_data(self, url, as_type='json', headers=None) -> bytes|dict|object:
        try:
            async with self._session.get(url, headers=headers,proxy=self.proxy) as r:
                data = await getattr(r, as_type)()
        except:
            error = traceback.format_exc()
            logging.error('Error, connect to url:%s.\n%s\n',url,error)
            return EMPTY_DATA
        else:
            logging.debug('finish request %s', url)
            return data
        

    async def init_client(self, proxy=None,conn_kwargs=None):
        connector = aiohttp.TCPConnector(**conn_kwargs) if conn_kwargs else aiohttp.TCPConnector()
        self._session = aiohttp.ClientSession(connector=connector)
        self.proxy = proxy
        if self.proxy is not None:
            await self.verify_proxy_server()

    async def _dead(self):
        await self.close()
        exit()

    async def close(self):
        await self._session.close()

    async def verify_proxy_server(self):
        try:
            logging.info('Test whether proxy config is correct,proxy server is {}'.format(self.proxy))
            url = 'https://api.github.com/users/littlezz'
            async with self._session.get(url, proxy=self.proxy) as r:
                status = r.status
                logging.info('test proxy status, [{}]'.format(status))
                assert r.status == 200
        except (aiohttp.ClientHttpProxyError, ConnectionRefusedError, AssertionError) as e:
            print('Proxy config is wrong!\n {}'.format(e))
            await self._dead()

client = _Client()