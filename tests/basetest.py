from island_backup import network
from island_backup.island_switcher import island_switcher
import aiohttp
import asyncio


async def get_page(url):
    network.session = aiohttp.ClientSession()
    island_switcher.detect_by_url(url)
    p = await island_switcher.island_page_model.from_url(url, page_num=1)
    network.session.close()
    return p


def check_block(block, data_dict):
    check_key = ['uid', 'id', 'content', 'image_url', 'created_time']
    for key in check_key:
        assert getattr(block, key) == data_dict[key]


class BaseTest:
    NEXT_PAGE_INFO = None
    THREAD_LIST_NUM = 20
    BLOCK_0_DATA = None
    BLOCK_1_DATA = None
    API_URL = ''

    def setup(self):
        self.page = asyncio.get_event_loop().run_until_complete(get_page(self.API_URL))

    def test_page(self):
        assert self.page.has_next()
        print(self.page.next_page_info)
        assert self.page.next_page_info == self.NEXT_PAGE_INFO

    def test_blocks_num(self):
        thread_list = self.page.thread_list()
        print(len(thread_list))
        assert len(thread_list) == self.THREAD_LIST_NUM


    def test_first_block(self):
        block = self.page.thread_list()[0]
        check_block(block, self.BLOCK_0_DATA)

    def test_second_block(self):
        block = self.page.thread_list()[1]
        check_block(block, self.BLOCK_1_DATA)

    def test_another_block(self):
        raise NotImplementedError
