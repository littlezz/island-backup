import os

import aiohttp
import asyncio
import re
import traceback
from functools import partial
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

#########setup#########
_conn = aiohttp.TCPConnector(use_dns_cache=True, limit=10, conn_timeout=60)
env = Environment(loader=FileSystemLoader('templates'), trim_blocks=True)



##########constant#########

# CDNHOST = 'http://hacfun-tv.n1.yun.tf:8999/Public/Upload'
CDNHOST = 'http://60.190.217.166:8999/Public/Upload'


_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Dnt': '1',
    'Host': 'hacfun-tv.n1.yun.tf:8999',
    'Pragma': 'no-cache',
    'Referer': 'http://h.nimingban.com/t/117617?page=10',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'}




def template_render(name, **context):
    return env.get_template(name).render(**context)


async def get_data(url, callback=None, as_type='json', conn=_conn, headers=None):
    try:
        async with aiohttp.get(url, connector=conn, headers=headers) as r:
            data = await getattr(r, as_type)()
            r.close()
    except Exception as e:
        print('exception!..', traceback.format_exc())
        data = ''

    print('finish request', url)
    if callback:
        asyncio.ensure_future(callback(data, url))
    else:
        return data


class ImageManager:
    def __init__(self, image_dir, loop, max_tasks=150):
        self.url_set = set()
        self.sem = asyncio.Semaphore(max_tasks)
        self.busying = set()
        self.loop = loop
        self.image_dir = image_dir

    def get_image_path(self, url):
        file_name = url.split('/')[-1]
        file_path = os.path.join(self.image_dir, file_name)
        return file_path

    async def submit(self, url):
        if url in self.url_set:
            return
        else:
            self.url_set.add(url)
        print('prepare download', url)
        file_path = self.get_image_path(url)

        if os.path.exists(file_path):
            return

        self.busying.add(url)
        await self.sem.acquire()
        # print('enter downloading')
        task = asyncio.ensure_future(get_data(url, as_type='read',
                                              headers=_headers,
                                              callback=partial(self.save_file, file_path=file_path)))
        task.add_done_callback(lambda t: self.sem.release())
        task.add_done_callback(lambda t: self.busying.remove(url))

    async def save_file(self, data, url, file_path):
        content = data
        if not content:
            print('no data available')
            return

        print('save file to ', file_path)

        with open(file_path, 'wb') as f:
            f.write(content)
        print('save success!')

    async def wait_all_task_done(self):
        print('begin waiting')
        while True:
            self.status_info()
            await asyncio.sleep(3)
            if not self.busying:
                break

        self.loop.stop()

    def status_info(self):
        print('this is {} in busying'.format(len(self.busying)))
        urls = []
        for i, url in enumerate(self.busying):
            if i >= 3:
                break
            urls.append(url)

        print('urls[3] is', urls)


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
        return self.base_url, page_num

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

    @property
    def created_time(self):
        ts = int(self._block['createdAt']) / 1000
        return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')


def sanitize_url(url):
    from urllib import parse
    parts = parse.urlsplit(url)
    path = '/api' + parts.path
    return parse.urlunsplit((parts.scheme, parts.netloc, path, '', ''))


def write_to_html(path, file_name, all_blocks, page_obj=None):
    thread_id = file_name
    file_name = file_name + '.html'
    save_to = os.path.join(path, file_name)
    with open(save_to, 'w', encoding='utf8') as f:
        f.write(template_render('base.html', title=thread_id, all_blocks=all_blocks, page_obj=page_obj))


def split_page_write(path, filename, blocks, page_num=50):
    if not page_num:
        write_to_html(path, filename, blocks)

    chunks = [blocks[i: i+page_num] for i in range(0, len(blocks), page_num)]
    max_page = len(chunks) - 1

    for idx, chunk in enumerate(chunks):
        page_filename = filename + '_' + str(idx)
        page_obj = {'prev': filename + '_' + str(idx-1) + '.html',
                    'next': filename + '_' + str(idx+1) + '.html'}
        if idx == 0:
            page_obj.pop('prev')
        if idx == max_page:
            page_obj.pop('next')
        write_to_html(path, page_filename, chunk, page_obj)


async def run(first_url, loop, base_dir=None, folder_name=None, image_manager=None):
    print('run!')

    all_blocks = []

    p = await Page.from_url(first_url, page_num=1)
    while True:
        print('page go')
        thread_list = p.thread_list()
        for block in thread_list:
            if block.image_url:
                asyncio.ensure_future(image_manager.submit(block.image_url))
                # print(block.uid, block.image_url, block.reply_to() or None)
                block.image = 'image/' + block.image.split('/')[-1]
        all_blocks.extend(thread_list)

        if p.has_next():
            p = await Page.from_url(*p.next_page_info)
        else:
            break

    split_page_write(path=base_dir, filename=folder_name, blocks=all_blocks, page_num=50)
    await image_manager.wait_all_task_done()


def main():

    first_url = input('url\n')
    # first_url = 'http://h.nimingban.com/t/117617'
    # first_url = 'http://h.nimingban.com/t/6048436?r=6048436'
    # first_url = 'http://h.nimingban.com/t/7317491?r=7317491'
    first_url = sanitize_url(first_url)
    folder_name = first_url.split('/')[-1]

    base_dir = os.path.join('backup', folder_name)
    image_dir = os.path.join(base_dir, 'image')
    os.makedirs(image_dir, exist_ok=True)

    print('first url is', first_url)
    loop = asyncio.get_event_loop()
    image_manager = ImageManager(image_dir, loop)
    loop.create_task(run(first_url, loop, base_dir=base_dir, image_manager=image_manager, folder_name=folder_name))
    loop.run_forever()


if __name__ == '__main__':
    main()
