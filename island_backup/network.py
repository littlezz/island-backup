import asyncio
import logging
import traceback
import aiohttp
from typing import Optional
from .utils import EMPTY_DATA


session: aiohttp.ClientSession|None = None
proxy = None


async def get_data(url, callback=None, as_type='json', headers=None, retry=3):
    _retry = 0
    _base = 2
    _log_error = None

    while _retry < retry:
        try:
            async with session.get(url, headers=headers,proxy=proxy) as r:
                data = await getattr(r, as_type)()
        except:
            # sleep 0s, 1s, 3s
            await asyncio.sleep(_base**_retry - 1)
            _retry += 1
            logging.debug('url: %s retry %s', url, _retry)
            _log_error = traceback.format_exc()
        else:
            break
    else:
        logging.error('\n Ignore Error:....\n%s\n...end\n', _log_error)
        print('Empyt data:',url)
        return EMPTY_DATA

    logging.debug('finish request %s', url)
    if callback:
        asyncio.create_task(callback(data, url))
    else:
        return data
    




class _Client:
    def __init__(self) -> None:
        self._session:aiohttp.ClientSession = None
        self.proxy = None

    async def get_data(self):
        pass

    async def init_client(self, proxy=None,conn_kwargs=None):
        connector = aiohttp.TCPConnector(**conn_kwargs) if conn_kwargs else aiohttp.TCPConnector()
        self._session = aiohttp.ClientSession(connector=connector)
        self.proxy = proxy
        try:
            logging.info('Test whether proxy config is correct')
            await self.verify_proxy_server()
        except (aiohttp.ClientHttpProxyError, ConnectionRefusedError, AssertionError) as e:
            print('Proxy config is wrong!\n {}'.format(e))
            exit()
    
    async def close(self):
        await self._session.close()

    async def verify_proxy_server(self):
        pass


client = _Client()