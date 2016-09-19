import asyncio
import logging
import traceback
from .utils import EMPTY_DATA


session = None


async def get_data(url, callback=None, as_type='json', headers=None, retry=3):
    _retry = 0
    _base = 2
    _log_error = None

    while _retry < retry:
        try:
            async with session.get(url, headers=headers) as r:
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
        print('Empyt data')
        return EMPTY_DATA

    logging.debug('finish request %s', url)
    if callback:
        asyncio.ensure_future(callback(data, url))
    else:
        return data