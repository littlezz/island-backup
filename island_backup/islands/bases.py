import asyncio

from datetime import datetime
from ..utils import EMPTY_DATA, url_page_combine
from ..network import get_data
import re


class BasePage:
    block_model = None

    def __init__(self, url=None, page_num=1, data=None):
        self._page = page_num
        self.base_url = url
        self.data = data

    @classmethod
    async def from_url(cls, base_url, page_num):
        data = await get_data(url_page_combine(base_url, page_num))
        if data is EMPTY_DATA:
            asyncio.get_event_loop().stop()

            exit('\nGot Connection Error!')
        return cls(base_url, page_num, data)

    def thread_list(self):
        """
        list of blocks
        :return:
        """
        raise NotImplementedError

    @property
    def next_page_num(self):
        if self.has_next():
            return self._page + 1

    @property
    def next_page_info(self):
        page_num = self._page + 1
        return self.base_url, page_num

    def has_next(self):
        return self._page < self.total_page

    @property
    def total_page(self):
        raise NotImplementedError


class BaseJsonPage(BasePage):

    @property
    def total_page(self):
        return self.data['page']['size']

    def thread_list(self):
        """
        list of blocks
        :return:
        """
        top = self.block_model(self.data['threads'])

        ext = [self.block_model(reply) for reply in self.data['replys']]
        ext.insert(0, top)
        return ext


class BaseBlock:
    """ proxy for div
    """
    request_info = dict()

    def __init__(self, block_data):
        self._block = block_data

    @property
    def id(self):
        raise NotImplementedError

    @property
    def uid(self):
        raise NotImplementedError

    @property
    def content(self):
        raise NotImplementedError

    def reply_to(self):
        """
        解析里面回复的id, 返回ids
        :return: list
        """
        return re.findall(r'No\.(\d+)', self.content)

    @property
    def image_url(self):
        """
        包含的image url
        :return:
        """
        raise NotImplementedError

    @property
    def created_time(self):
        raise NotImplementedError

    @property
    def cdn_host(self):
        return self.request_info['cdn_host']

    @property
    def headers(self):
        return self.request_info['headers']



class BaseJsonBlock(BaseBlock):
    @property
    def id(self):
        return self._block.get('id')

    @property
    def uid(self):
        return self._block.get('uid')

    @property
    def content(self):
        return self._block.get('content')

    @property
    def image_url(self):
        """
        包含的image url
        :return:
        """
        url = self._block.get('image')
        if not url:
            return None
        return ''.join((self.cdn_host, url))

    @property
    def created_time(self):
        ts = int(self._block['createdAt']) / 1000
        return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')