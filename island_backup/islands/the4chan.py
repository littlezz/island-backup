import re
from urllib import parse
from .bases import BaseJsonBlock, BaseJsonPage
import os.path


JSON_CDN = 'http://a.4cdn.org'

class The4ChanBlock(BaseJsonBlock):
    request_info = {
        'cdn_host': 'http://i.4cdn.org',
        'headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Dnt': '1',
            'Pragma': 'no-cache',
            'Host': 'i.4cdn.org',
            'Referer': 'http://boards.4chan.org/',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'
        }
    }

    def __init__(self, block_data, broad=None):
        super().__init__(block_data=block_data)
        self.broad = broad

    @property
    def id(self):
        return self._block.get('no', '')

    @property
    def uid(self):
        return self._block.get('name', '')

    def _get_content(self):
        return self._block.get('com', '')

    def _deal_with_reply(self, content):
        return content

    @property
    def image_url(self):
        tim = self._block.get('tim', None)
        if not tim:
            return None
        ext = self._block['ext']

        image_name = str(tim) + ext
        url = '/'.join((self.request_info['cdn_host'], self.broad, image_name))
        return url

    @property
    def created_time(self):
        return self._block['now']



class The4ChanPage(BaseJsonPage):
    block_model = The4ChanBlock
    def has_next(self):
        return False

    @property
    def total_page(self):
        return None

    @staticmethod
    def url_page_combine(base_url, page_num):
        return base_url

    @staticmethod
    def get_thread_id(url):
        return re.match(r'.*/thread/(\d+)', url).group(1)

    @staticmethod
    def _get_broad_short_name(url):
        return parse.urlparse(url).path.split('/')[1]

    def thread_list(self):
        posts = self.data['posts']
        broad = self._get_broad_short_name(self.base_url)
        return [self.block_model(block_data=b, broad=broad) for b in posts]

    @staticmethod
    def sanitize_url(url):
        path = re.match('.*/\d+', parse.urlparse(url).path).group() + '.json'
        return parse.urljoin(JSON_CDN, path)
