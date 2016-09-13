import pytest
from island_backup.main import Page, island_switcher
import asyncio

from tests.basetest import *


async def x():
    island_switcher.detect_by_url('http://h.adnmb.com/api/t/106983')
    print(island_switcher.island)
    p = await Page.from_url('http://h.adnmb.com/api/t/106983', page_num=1)
    return p


@pytest.fixture()
def page():
    p = asyncio.get_event_loop().run_until_complete(x())
    return p

class TestAdnmb(BaseTest):
    NEXT_PAGE_INFO = ('http://h.adnmb.com/api/t/106983', 2)
    IMAGE_URL_1 = 'http://h-adnmb-com.n1.yun.tf:8999/Public/Upload/image/2016-05-14/57372d96e74c2.jpg'
    IMAGE_URL_2 = 'http://h-adnmb-com.n1.yun.tf:8999/Public/Upload/image/2016-05-14/57373100c6017.png'
    THREAD_LIST_NUM = 21

    def test_block(self, page):
        thread_list = page.thread_list()
        print(len(thread_list))
        assert len(thread_list) == self.THREAD_LIST_NUM
        block = thread_list[0]
        assert block.image_url == self.IMAGE_URL_1
        assert thread_list[1].image_url == None
        assert thread_list[7].image_url == self.IMAGE_URL_2


def atest_tmp(tmpdir):
    a = tmpdir.mkdir('sub')
    with open(str(a) + '/xx.txt', 'w') as f:
        f.write('?')
    c= a.join('xx.txt')
    print(c.read())
    print(a)
    assert 0


# print(asyncio.get_event_loop().run_until_complete(x()))