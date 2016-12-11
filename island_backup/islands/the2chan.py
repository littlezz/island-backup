from .bases import BasePage, BaseBlock
from bs4 import BeautifulSoup
import re


class The2ChanBlock(BaseBlock):
    request_info = {
        'cdn_host': None,
        'headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Dnt': '1',
            'Host': 'img1.nimingban.com',
            'Pragma': 'no-cache',
            'Referer': 'http://h.nimingban.com/t/117617?page=10',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'
        }
    }

    @property
    def id(self):
        return self._block.find('').text