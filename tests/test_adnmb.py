import pytest
from island_backup.main import Page, island_switcher
import asyncio

from tests.basetest import *


async def prepare_page():
    island_switcher.detect_by_url('http://h.adnmb.com/api/t/106983')
    p = await Page.from_url('http://h.adnmb.com/api/t/106983', page_num=1)
    return p


@pytest.fixture(scope='module')
def page():
    p = asyncio.get_event_loop().run_until_complete(prepare_page())
    return p



class TestAdnmb(BaseTest):
    NEXT_PAGE_INFO = ('http://h.adnmb.com/api/t/106983', 2)
    BLOCK_0_IMAGE_URL = 'http://h-adnmb-com.n1.yun.tf:8999/Public/Upload/image/2016-05-14/57372d96e74c2.jpg'
    BLOCK_1_IMAGE_URL = None
    THREAD_LIST_NUM = 21


    def test_another_block(self, page):
        block = page.thread_list()[7]
        assert block.image_url == 'http://h-adnmb-com.n1.yun.tf:8999/Public/Upload/image/2016-05-14/57373100c6017.png'


def atest_tmp(tmpdir):
    a = tmpdir.mkdir('sub')
    with open(str(a) + '/xx.txt', 'w') as f:
        f.write('?')
    c= a.join('xx.txt')
    print(c.read())
    print(a)
    assert 0

