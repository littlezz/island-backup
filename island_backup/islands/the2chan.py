from .bases import BasePage, BaseBlock
from bs4 import BeautifulSoup
import re
from urllib import parse


def openbr2closebr(html: str):
    return html.replace('<br>', '<br/>')


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
            'Pragma': 'no-cache',
            'Referer': 'http://www.2chan.net/',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'
        }
    }

    def __init__(self, block_data, page_domain):
        super().__init__(block_data)
        self._page_domain = page_domain

    @property
    def id(self):
        info_string = self._block.find('a', class_='del').previous
        return info_string[info_string.find('No')+3:].strip()

    @property
    def uid(self):
        return self._block.find('font', color='#117743').text
    
    @property
    def created_time(self):
        info_string = self._block.find('a', class_='del').previous
        return info_string[: info_string.find('No')].strip()

    def _get_content(self):
        div = self._block.find('blockquote')
        return ''.join(str(e).strip() for e in div.contents)

    def _deal_with_reply(self, content):
        return re.sub(r'<font color.*?>(.*?)</font>', r'<span class="reply-color">\1</span>', content)

    @property
    def image_url(self):
        tag = self._block.find('a', target='_blank')
        if not tag:
            return None
        path = tag.attrs.get('href')
        url = parse.urljoin(self._page_domain, path)
        return url


class The2ChanFirstBlock(The2ChanBlock):
    @property
    def image_url(self):
        tag = self._block.find('a', target='_blank', recursive=False)
        if not tag:
            return None
        path = tag.attrs.get('href')
        url = parse.urljoin(self._page_domain, path)
        return url



class The2ChanPage(BasePage):
    block_model = The2ChanBlock

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        html = openbr2closebr(self.data)
        self.bs = BeautifulSoup(html, 'html.parser')

    @staticmethod
    def url_page_combine(base_url, page_num):
        return base_url

    def has_next(self):
        return False

    @property
    def total_page(self):
        return None

    @staticmethod
    def get_thread_id(url):
        return re.match(r'.*?/(\d+)\.htm', url).group(1)

    def thread_list(self):
        domain = parse.urljoin(self.base_url, '/')
        top = The2ChanFirstBlock(self.bs.find(class_='thre'), page_domain=domain)
        threads = [self.block_model(b, page_domain=domain) for b in self.bs.find_all('td', class_='rtd')]
        threads.insert(0, top)
        return threads

    @staticmethod
    def sanitize_url(url):
        parts = parse.urlparse(url)
        return '{0.scheme}://{0.netloc}{0.path}'.format(parts)