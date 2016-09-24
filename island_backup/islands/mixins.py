import re


class AIslandGetThreadId:

    @staticmethod
    def get_thread_id(url):
        return re.match(r'.*/t/(\d+)', url).group(1)