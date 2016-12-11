from tests.basetest import *


class TestNiMingBan(BaseTest):

    REQUEST_URLS = ['https://h.nimingban.com/t/9800114?page=1']
    RAW_URLS = ['https://h.nimingban.com/t/9800114']
    NEXT_PAGE_URL = 'https://h.nimingban.com/t/9800114?page=2'
    THREAD_LIST_NUM = 20
    BLOCK_0_DATA = {
        'image_url': 'http://cdn.ovear.info:8998/image/2016-09-18/57de3d443bce3.jpg',
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

    def test_another_block(self, thread_list):
        b = thread_list[4]
        assert b.content == """<span class="reply-color"><font color="#789922">&gt;&gt;No.9800114</font></span><br/>……出题老师可以的"""
