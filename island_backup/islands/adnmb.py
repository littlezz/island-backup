from .bases import BaseJsonPage, BaseJsonBlock
from .mixins import AIslandGetThreadId
import re

__all__ = ['AdnmbBlock', 'AdnmbPage']


_request_info = {
    'cdn_host': 'http://h-adnmb-com.n1.yun.tf:8999/Public/Upload',
    'headers': {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Dnt': '1',
        'Host': 'h-adnmb-com.n1.yun.tf:8999',
        'Pragma': 'no-cache',
        'Referer': 'http://h.adnmb.com/',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
    }
}


class AdnmbBlock(BaseJsonBlock):
    request_info = _request_info

    def _deal_with_reply(self, content):
        return re.sub(r'(<font color.*?>.*?\d+</font>)', r'<span class="reply-color">\1</span>', content)

class AdnmbPage(AIslandGetThreadId, BaseJsonPage):
    block_model = AdnmbBlock