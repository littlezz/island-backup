from island_backup import network
from island_backup.island_switcher import island_switcher
import aiohttp
import asyncio
import pytest


NO_NEXT_PAGE = object()



async def get_page(url):
    network.session = aiohttp.ClientSession()
    island_switcher.detect_by_url(url)
    url = island_switcher.sanitize_url(url)
    print(url)
    p = await island_switcher.island_page_model.from_url(url, page_num=1)
    network.session.close()
    return p


def check_block(block, data_dict):
    check_key = ['uid', 'id', 'content', 'image_url', 'created_time']
    for key in check_key:
        assert getattr(block, key) == data_dict[key]


class BaseTest:
    NEXT_PAGE_URL = ''
    THREAD_LIST_NUM = 20
    BLOCK_0_DATA = None
    BLOCK_1_DATA = None
    # 原始用户输入的URL
    RAW_URLS = None
    # 转换后程序应该请求的URL， 与RAW_URLS一一对应。
    REQUEST_URLS = None

    @pytest.fixture(scope='class')
    def page(self):
        return asyncio.get_event_loop().run_until_complete(get_page(self.RAW_URLS[0]))

    @pytest.fixture(scope='class')
    def thread_list(self, page):
        return page.thread_list()


    def test_sanitize_url(self, page):
        for raw, req in zip(self.RAW_URLS, self.REQUEST_URLS):
            assert page.url_page_combine(page.sanitize_url(raw), 1) == req

    def test_page(self, page):
        if self.NEXT_PAGE_URL is NO_NEXT_PAGE:
            return

        assert page.has_next()
        print(page.next_page_info)
        assert page.url_page_combine(*page.next_page_info) == self.NEXT_PAGE_URL

    def test_blocks_num(self, thread_list):
        print(len(thread_list))
        assert len(thread_list) == self.THREAD_LIST_NUM


    def test_first_block(self, thread_list):
        block = thread_list[0]
        check_block(block, self.BLOCK_0_DATA)

    def test_second_block(self, thread_list):
        block = thread_list[1]
        check_block(block, self.BLOCK_1_DATA)

    def test_another_block(self, thread_list):
        raise NotImplementedError
