import asyncio
from datetime import datetime
from ..utils import EMPTY_DATA
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
        # always request first page url
        data = await get_data(cls.url_page_combine(base_url, page_num), as_type='text')
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

    @staticmethod
    def get_thread_id(url):
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
        raise NotImplementedError

    @staticmethod
    def url_page_combine(base_url, page_num):
        raise NotImplementedError

    @staticmethod
    def sanitize_url(url):
        raise NotImplementedError

    @property
    def total_page(self):
        raise NotImplementedError



class BaseJsonPage(BasePage):
    request_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Dnt': '1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.87 Safari/537.36'
    }


    @classmethod
    async def from_url(cls, base_url, page_num):
        data = await get_data(cls.url_page_combine(base_url, page_num), as_type='json', headers=cls.request_headers)
        if data is EMPTY_DATA:
            asyncio.get_event_loop().stop()

            exit('\nGot Connection Error!')
        return cls(base_url, page_num, data)

    @staticmethod
    def url_page_combine(base_url, page_num):
        return base_url + '?page=' + str(page_num)

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

    def has_next(self):
        return self._page < self.total_page

    @staticmethod
    def sanitize_url(url):
        from urllib import parse
        parts = parse.urlsplit(url)
        path = '/api' + parts.path
        return parse.urlunsplit((parts.scheme, parts.netloc, path, '', ''))


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
        content = self._get_content()
        return self._deal_with_reply(content=content)

    def _get_content(self):
        raise NotImplementedError

    def _deal_with_reply(self, content):
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

    def _get_content(self):
        return self._block.get('content')

    def _deal_with_reply(self, content):
        return content

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