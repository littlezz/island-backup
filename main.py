import aiohttp
import asyncio
from asyncio import coroutine
import jinja2
import re


CDNHOST = 'http://hacfun-tv.n1.yun.tf:8999/Public/Upload'


async def get_data(url, callback=None, as_type='json'):
    # r = await aiohttp.get(url)
    # data = await getattr(r, as_type)()
    async with aiohttp.get(url) as r:
        data = await getattr(r, as_type)()

    print('finish request', url)
    if callback:
        asyncio.ensure_future(callback(data, url))
    else:
        return data




class ImageManager:
    def __init__(self, loop, max_tasks=100):
        self.url_set  = set()
        self.sem = asyncio.Semaphore(max_tasks)
        self.busying = set()
        self.loop = loop

    async def submit(self, url):
        if url in self.url_set:
            return
        else:
            self.url_set.add(url)
        print('prepare download', url)
        file_name = url.split('/')[-1]
        file_path = 'image/' + file_name
        await self.sem.acquire()
        print('enter downloading')
        task = asyncio.ensure_future(get_data(url, as_type='read'))
        self.busying.add(task)
        task.add_done_callback(lambda t:self.sem.release())
        task.add_done_callback(lambda t:self.save_file(task=t, file_path=file_path))
        task.add_done_callback(self.busying.remove)

    def save_file(self, task, file_path):
        print('save file to ', file_path)
        try:
            content = task.result()
        except Exception as e:
            print('got exception!', e)
            return

        with open(file_path, 'wb') as f:
            f.write(content)
        print('sace sucess!')

    async def wait_all_task_done(self):
        print('begin waiting')
        while True:
            await asyncio.sleep(1)
            if not self.busying:
                break

        self.loop.stop()


def url_page_combine(base_url, num):
    return base_url + '?page=' + str(num)




class Page:
    def __init__(self, url=None, page_num=1, data=None):
        self._page = page_num
        self.base_url = url
        self.data = data



    @classmethod
    async def from_url(cls, base_url, page_num):
        data = await get_data(url_page_combine(base_url, page_num))
        return cls(base_url, page_num, data)

    def thread_list(self):
        """
        list of blocks
        :return:
        """
        top = Block(self.data['threads'])

        ext = [Block(reply) for reply in self.data['replys']]
        ext.insert(0, top)
        return ext



    @property
    def next_page_num(self):
        if self.has_next():
            return self._page + 1


    @property
    def next_page_info(self):
        page_num = self._page + 1
        return (self.base_url, page_num)

    def has_next(self):
        return self._page < self.data['page']['size']




class Block:
    """ proxy for div
    """
    def __init__(self, block_dict):
        self._block = block_dict


    def __getattr__(self, item):
        return self._block.get(item)




    def reply_to(self):
        """
        解析里面回复的id, 返回ids
        :return: list
        """
        return re.findall(r'No\.(\d+)', self.content)


    @property
    def image_url(self):
        """
        包含的image url
        :return:
        """
        if not self.image:
            return None
        return ''.join((CDNHOST, self.image))

    def replace_image_url(self, path):
        """
        替换里面的url标签的内容为cache的图片地址
        :param path:
        :return:
        """


def sanitize_url(url):

    return url



async def run(first_url, loop):
    print('run!')
    p = await Page.from_url(first_url, page_num=1)
    while True:
        print('page go')
        thread_list = p.thread_list()
        for block in thread_list:
            if block.image_url:
                asyncio.ensure_future(image_manager.submit(block.image_url))
            print(block.uid, block.image_url, block.reply_to() or None)
        if p.has_next():
            p=await Page.from_url(*p.next_page_info)

        if p.next_page_num > 15:
            break
    await image_manager.wait_all_task_done()



# url = input()
# first_url = sanitize_url(url)
# first_url = 'http://h.nimingban.com/api/t/7250124'
first_url = 'http://h.nimingban.com/api/t/103123'
# while True:
#     p = Page(url)
#     blocks = p.thread_list()
#     for b in blocks:
#         b.do_something()
#
#     if p.has_next():
#         p = Page(p.next_page_url)
#     else:
#         break

loop = asyncio.get_event_loop()
image_manager = ImageManager(loop)
loop.create_task(run(first_url, loop))

loop.run_forever()

