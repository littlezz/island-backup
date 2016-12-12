from .basetest import *



class Test2Chan(BaseTest):
    REQUEST_URLS = ['http://dec.2chan.net/62/res/29194.htm']
    RAW_URLS = ['http://dec.2chan.net/62/res/29194.htm']
    NEXT_PAGE_URL = NO_NEXT_PAGE
    THREAD_LIST_NUM = 20

    # We fix <br> to <br/> in program
    BLOCK_0_DATA = {
        'image_url': 'http://dec.2chan.net/62/src/1479904149860.jpg',
        'uid': '名無し ',
        'id': '29194',
        'created_time': '16/11/23(水)21:29:09',
        'content': """CB缶ですよ！これからは<br/>…寒くて火力があぁぁぁぁ"""
    }
    BLOCK_1_DATA = {
        'image_url': None,
        'uid': '名無し ',
        'id': '29196',
        'created_time': '16/11/23(水)21:40:16',
        'content': """プレヒートが面倒だけど、ヒートパイプ付最強<br/>高所でも厳寒地でも使える"""
    }

    def test_another_block(self, thread_list):
        b = thread_list[8]
        assert b.content == """細かいことは良いんだよ<br/>普通のガス缶使えや"""
        assert b.image_url == "http://dec.2chan.net/62/src/1479908468315.jpg"

    def test_blocks_num(self, thread_list):
        pass