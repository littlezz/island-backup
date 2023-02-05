from tests.basetest import *


class TestNiMingBan(BaseTest):

    REQUEST_URLS = ['https://www.nmbxd1.com/t/55333001?page=1']
    RAW_URLS = ['https://www.nmbxd1.com/t/55333001?r=55333007']
    NEXT_PAGE_URL = 'https://www.nmbxd1.com/t/55333001?page=2'
    THREAD_LIST_NUM = 20
    BLOCK_0_DATA = {
        'image_url': 'https://image.nmb.best/image/2023-02-05/63deb1222752d.jpg',
        'uid': 'wkd6djc',
        'id': '55333001',
        'created_time': '2023-02-05 03:25:20',
        'content': """凌晨，空无一人的候车大厅，车票对应的检票口显示屏乱码"""
    }
    BLOCK_1_DATA = {
        'image_url': None,
        'uid': 'wkd6djc',
        'id': '55333007',
        'created_time': '2023-02-05 03:26:06',
        'content': "( ﾟ∀。)7要不还是买下一班车的票吧？"
    }

    def test_another_block(self, thread_list):
        b = thread_list[3]
        assert b.content == """这乱码乱出来的图案还挺整齐的(´ﾟДﾟ`)"""
