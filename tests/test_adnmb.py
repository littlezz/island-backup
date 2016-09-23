import pytest
import asyncio

from tests.basetest import *





class TestAdnmb(BaseTest):
    RAW_URLS = ['http://h.adnmb.com/t/106983']
    REQUEST_URLS = ['http://h.adnmb.com/api/t/106983?page=1']
    NEXT_PAGE_URL = 'http://h.adnmb.com/api/t/106983?page=2'
    THREAD_LIST_NUM = 21
    BLOCK_0_DATA = {
        'image_url': 'http://h-adnmb-com.n1.yun.tf:8999/Public/Upload/image/2016-05-14/57372d96e74c2.jpg',
        'uid': 'W0wrx3S',
        'id': '106983',
        'content': """|∀ﾟ有广东的肥肥吗，我好想买，可惜我这里暂时没有""",
        'created_time': '2016-05-14 21:52:23'
    }
    BLOCK_1_DATA = {
        'image_url': None,
        'uid': 'dPRC8y8',
        'content': """大吃人在此，不过我用的是移动| ω・´)""",
        'id': '106987',
        'created_time': '2016-05-14 21:56:00',
    }


    def test_another_block(self, thread_list):
        block = thread_list[7]
        assert block.image_url == 'http://h-adnmb-com.n1.yun.tf:8999/Public/Upload/image/2016-05-14/57373100c6017.png'


def atest_tmp(tmpdir):
    a = tmpdir.mkdir('sub')
    with open(str(a) + '/xx.txt', 'w') as f:
        f.write('?')
    c= a.join('xx.txt')
    print(c.read())
    print(a)
    assert 0

