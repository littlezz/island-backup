from .basetest import *

class TestKukuku(BaseTest):
    RAW_URLS = ['http://www.kukuku.cc/t/6934861/1', 'http://www.kukuku.cc/t/6934861']
    REQUEST_URLS = ['http://www.kukuku.cc/t/6934861/1', 'http://www.kukuku.cc/t/6934861/1']
    NEXT_PAGE_URL = 'http://www.kukuku.cc/t/6934861/2'
    THREAD_LIST_NUM = 21
    BLOCK_0_DATA = {
        'image_url': 'http://static.kukuku.cc/FoU6oNXFNKbMNvzAw_kRfmcFeze5.jpeg',
        'uid': 'JxpxDCEjXM',
        'id': '6934861',
        'created_time': '2016-09-07 17:42:39',
        'content': '''(;´Д`)宿舍门口有只超骚的小主子，想要撩撩它，应该拿什么喂它或者逗它(=ﾟωﾟ)=''',
    }
    BLOCK_1_DATA = {
        'image_url': None,
        'uid': 'WudUsohuEP',
        'id': '10209793',
        'created_time': '2016-09-07 18:30:29',
        'content': """斯大林主子(ﾟДﾟ≡ﾟДﾟ)""",
    }

    def test_another_block(self):
        pass