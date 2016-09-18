from island_backup import main
from island_backup.main import island_switcher, Page
import aiohttp


class BasePreparePage:
    API_URL = None
    async def get_page(self):
        main.session = aiohttp.ClientSession()
        island_switcher.detect_by_url(self.API_URL)
        p = await Page.from_url(self.API_URL, page_num=1)
        main.session.close()
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

    def test_page(self, page):
        assert page.has_next()
        print(page.next_page_info)
        assert page.next_page_info == self.NEXT_PAGE_INFO

    def test_blocks_num(self, page):
        thread_list = page.thread_list()
        print(len(thread_list))
        assert len(thread_list) == self.THREAD_LIST_NUM


    def test_first_block(self, page):
        block = page.thread_list()[0]
        check_block(block, self.BLOCK_0_DATA)

    def test_second_block(self, page):
        block = page.thread_list()[1]
        check_block(block, self.BLOCK_1_DATA)

    def test_another_block(self, page):
        raise NotImplementedError
