from .basetest import *


class Test4Chan(BaseTest):
    RAW_URLS = ['http://boards.4chan.org/u/thread/1436960/welcome-to-u', 'http://boards.4chan.org/u/thread/1436960']
    REQUEST_URLS = ['http://a.4cdn.org/u/thread/1436960.json', 'http://a.4cdn.org/u/thread/1436960.json']
    NEXT_PAGE_URL = None
    THREAD_LIST_NUM = None
    BLOCK_0_DATA = {
        'image_url': 'http://i.4cdn.org/u/1376789114258.jpg',
        'uid': 'Anonymous',
        'id': '1436960',
        'created_time': '08/18/13(Sun)09:25:14',
        'content':
            '''/u/ is for discussions about the yuri genre of manga, anime, and other related media. Threads requesting images or series recommendations are discouraged \
            (try <a href="https://boards.4chan.org/r/">>>>/r/</a> instead). When starting an image dump thread, please contribute at least 4-5 relevant images yourself. \
            <br><br>Where to read manga: <br><a href="http://dynasty-scans.com/">http://dynasty-scans.com/</a><br><br>Some notable scanlators:<br><a href="http://www.lili\
            licious.net/">http://www.lililicious.net/</a><br><a href="http://yuri-ism.com/">http://yuri-ism.com/</a><br><a href="http://yuriproject.net/">http://yuriproje\
            ct.net/</a><br><br>Just getting into the yuri genre, or just looking for recommendations? Click [Reply] for /u/ guides to manga, anime, and live action.''',

    }
    BLOCK_1_DATA = {
        'image_url': 'http://i.4cdn.org/u/1376789154203.png',
        'uid': 'Anonymous',
        'id': '1436961',
        'created_time': '08/18/13(Sun)09:25:54',
        'content': """These charts are intended to provide major introductory material and are by no means all-encompassing.<br><br>Where to start with yuri manga.""",
    }

    def test_another_block(self, thread_list):
        pass
