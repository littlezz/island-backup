import pytest


ay = pytest.mark.asyncio


class BaseTest:
    NEXT_PAGE_INFO = None
    THREAD_LIST_NUM = 20

    def test_page(self, page):
        assert page.has_next()
        print(page.next_page_info)
        assert page.next_page_info == self.NEXT_PAGE_INFO


    def test_block(self, page):
        pass