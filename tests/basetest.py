class BaseTest:
    NEXT_PAGE_INFO = None
    THREAD_LIST_NUM = 20
    BLOCK_0_IMAGE_URL = None
    BLOCK_1_IMAGE_URL = None

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
        assert block.image_url == self.BLOCK_0_IMAGE_URL

    def test_second_block(self, page):
        block = page.thread_list()[1]
        assert block.image_url == self.BLOCK_1_IMAGE_URL
