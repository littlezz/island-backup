from .bases import BasePage, BaseBlock
from bs4 import BeautifulSoup
import re
from .mixins import AIslandGetThreadId


class NiMingBanBlock(BaseBlock):
    request_info = {
        'cdn_host': 'http://img1.nimingban.com',
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
        return self._block.find('a', class_='h-threads-info-id').text.split('.')[-1]

    @property
    def uid(self):
        return self._block.find('span', class_='h-threads-info-uid').text.split(':')[-1]

    def _get_content(self):
        div = self._block.find('div', class_='h-threads-content')
        return ''.join(str(e).strip() for e in div.contents)

    def _deal_with_reply(self, content):
        return re.sub(r'(<font color.*?>.*?\d+</font>)', r'<span class="reply-color">\1</span>', content)

    @property
    def created_time(self):
        # ex, get 2012-10-23(二)01:20:54
        s = self._block.find('span', class_='h-threads-info-createdat').text
        # replace number in parentheses to space
        return re.sub(r'\(.\)', ' ', s)

    @property
    def image_url(self):
        tag = self._block.find('a', class_='h-threads-img-a')
        if tag:
            return tag.attrs.get('href')
        else:
            return None


class NiMingBanPage(AIslandGetThreadId, BasePage):
    block_model = NiMingBanBlock

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bs = BeautifulSoup(self.data, 'html.parser')
        # self.bs = BeautifulSoup(self.data, 'lxml')

    @staticmethod
    def url_page_combine(base_url, page_num):
        return base_url + '?page=' + str(page_num)

    def thread_list(self):
        top = self.block_model(self.bs.find(class_='h-threads-item-main'))
        threads = [self.block_model(b) for b in self.bs.find_all(class_='h-threads-item-reply')]
        threads.insert(0, top)
        return threads

    def has_next(self):
        if self.bs.find('a', text='下一页'):
            return True
        return False

    @property
    def total_page(self):
        return None

    @staticmethod
    def sanitize_url(url):

        # remove useless query
        url = url.rsplit('?')[0]
        return url
