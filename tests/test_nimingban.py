from tests.basetest import *


class TestNiMingBan(BaseTest):
    API_URL = 'https://h.nimingban.com/api/t/9800114'
    NEXT_PAGE_INFO = ('https://h.nimingban.com/api/t/9800114', 2)
    THREAD_LIST_NUM = 21
    BLOCK_0_DATA = {
        'image_url': 'http://img1.nimingban.com/image/2016-09-18/57de3d443bce3.jpg',
        'uid': '4ZzUhjy',
        'id': '9800114',
        'created_time': '2016-09-18 15:07:48',
        'content': """下个星期就考了，好慌"""
    }
    BLOCK_1_DATA = {
        'image_url': None,
        'uid': 'JvnJBG5',
        'id': '9800148',
        'created_time': '2016-09-18 15:11:07',
        'content': '选b啊！！'
    }

    def test_another_block(self):
        pass
