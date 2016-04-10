import os
import sys
import aiohttp
import asyncio
import re
import traceback
from functools import partial
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import click
from tqdm import tqdm
import logging
from . import version as __version__
logging.basicConfig(level=logging.INFO, format='{asctime}: {message}', style='{')


##########constant#########


_island_info = {
    'nimingban': {
        'CDNHOST': 'http://img1.nimingban.com',
        'headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Dnt': '1',
            'Host': 'img1.nimingban.com',
            'Pragma': 'no-cache',
            'Referer': 'http://h.nimingban.com/t/117617?page=10',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'
            }
        },
    'kukuku': {
        'CDNHOST': 'http://static.koukuko.com/h',
        'headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Dnt': '1',
            'Host': 'static.koukuko.com',
            'Pragma': 'no-cache',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36'
            }
    }
}



#########setup#########


bundle_env = getattr(sys, 'frozen', False)

if bundle_env:
    BASE = sys._MEIPASS
else:
    BASE = os.path.dirname(__file__)


env = Environment(loader=FileSystemLoader(os.path.join(BASE, 'templates')), trim_blocks=True)


################


class IslandSwitcher:
    available_island = ['nimingban', 'kukuku']

    def __init__(self, island='nimingban'):
        assert island in self.available_island
        self.island = island

    def detect_by_url(self, url):
        for island in self.available_island:
            if island in url:
                self.island = island
                return
        raise ValueError('Unknown url: {}'.format(url))

    @property
    def cdn_host(self):
        return _island_info[self.island]['CDNHOST']

    @property
    def headers(self):
        return _island_info[self.island]['headers']


island_switcher = IslandSwitcher()


def template_render(name, **context):
    return env.get_template(name).render(**context)


async def get_data(url, callback=None, as_type='json', headers=None):
    try:
        async with session.get(url, headers=headers) as r:
            data = await getattr(r, as_type)()
    except Exception as e:
        logging.ERROR('exception!.. %s', traceback.format_exc())
        data = ''

    logging.debug('finish request %s', url)
    if callback:
        asyncio.ensure_future(callback(data, url))
    else:
        return data


class ImageManager:
    def __init__(self, image_dir, loop, max_tasks=150, force_update=False):
        self.url_set = set()
        self.sem = asyncio.Semaphore(max_tasks)
        self.busying = set()
        self.loop = loop
        self.image_dir = image_dir
        self.pdbar = tqdm(desc='image downloading...', position=1)
        # force update image
        self.force_update = force_update

    def get_image_path(self, url):
        file_name = url.split('/')[-1]
        file_path = os.path.join(self.image_dir, file_name)
        return file_path

    async def submit(self, url):
        if url in self.url_set:
            return
        else:
            self.url_set.add(url)
        logging.debug('prepare download %s', url)
        file_path = self.get_image_path(url)

        if not self.force_update and os.path.exists(file_path):
            return

        self.busying.add(url)
        await self.sem.acquire()
        task = asyncio.ensure_future(get_data(url, as_type='read',
                                              headers=island_switcher.headers,
                                              callback=partial(self.save_file, file_path=file_path)))

        task.add_done_callback(lambda t: self.sem.release())
        task.add_done_callback(lambda t: self.busying.remove(url))
        task.add_done_callback(lambda t: self.status_info())

    async def save_file(self, data, url, file_path):
        content = data
        if not content:
            logging.debug('no data available')
            return

        logging.debug('save file to %s', file_path)

        with open(file_path, 'wb') as f:
            f.write(content)

    async def wait_all_task_done(self):
        logging.debug('begin waiting')
        while True:
            await asyncio.sleep(3)
            if not self.busying:
                break
        self.loop.stop()

    def status_info(self):
        self.pdbar.update()

        logging.debug('this is {} in busying'.format(len(self.busying)))
        urls = []
        for i, url in enumerate(self.busying):
            if i >= 3:
                break
            urls.append(url)

        logging.debug('urls[3] is %s', urls)


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
        return self._page < self.total_page

    @property
    def total_page(self):
        return self.data['page']['size']


class Block:
    """ proxy for div
    """
    def __init__(self, block_dict):
        self._block = block_dict

    def __getattr__(self, item):
        # property proxy for json data
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
        return ''.join((island_switcher.cdn_host, self.image))

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
    all_blocks = []
    p = await Page.from_url(first_url, page_num=1)
    process_bar = tqdm(total=p.total_page, position=0, desc='page scanning')
    process_bar.update()
    while True:
        thread_list = p.thread_list()
        for block in thread_list:
            if block.image_url:
                asyncio.ensure_future(image_manager.submit(block.image_url))
                block.image = 'image/' + block.image.split('/')[-1]
        all_blocks.extend(thread_list)

        if p.has_next():
            p = await Page.from_url(*p.next_page_info)
            process_bar.update()
        else:
            break

    split_page_write(path=base_dir, filename=folder_name, blocks=all_blocks, page_num=50)
    await image_manager.wait_all_task_done()
    process_bar.close()


def start(url, force_update, _conn):

    global session
    session = aiohttp.ClientSession(connector=_conn)

    first_url = url
    # first_url = 'http://h.nimingban.com/t/117617'
    # first_url = 'http://h.nimingban.com/t/6048436?r=6048436'
    # first_url = 'http://h.nimingban.com/t/7317491?r=7317491'
    first_url = sanitize_url(first_url)
    island_switcher.detect_by_url(first_url)
    folder_name = island_switcher.island + '_' + first_url.split('/')[-1]

    base_dir = os.path.join('backup', folder_name)
    image_dir = os.path.join(base_dir, 'image')
    os.makedirs(image_dir, exist_ok=True)

    logging.info('url is %s', first_url)
    logging.info('island is %s', island_switcher.island)
    loop = asyncio.get_event_loop()
    image_manager = ImageManager(image_dir, loop, force_update=force_update)
    loop.create_task(run(first_url, loop, base_dir=base_dir, image_manager=image_manager, folder_name=folder_name))
    loop.run_forever()
    session.close()


def cli_url_verify(ctx, param, value):
    if value is None:
        return
    if not any(i in value for i in IslandSwitcher.available_island):
        raise click.BadParameter('Unsupported url {}:'.format(value))
    return value


@click.command()
@click.argument('url', required=False, callback=cli_url_verify)
@click.option('-url', prompt='Please Input Url', callback=cli_url_verify)
@click.option('--debug', is_flag=True, help='enable debug mode')
@click.option('--force-update', is_flag=True, help='force update image')
@click.option('--conn-count', type=click.IntRange(1, 20), help='conn number connector use. from 1 to 20.')
@click.version_option(version=__version__)
def cli(url, debug, force_update, conn_count):
    if debug:
        logging.root.setLevel(logging.DEBUG)

    logging.info('conn number is %s', conn_count)

    _conn = aiohttp.TCPConnector(use_dns_cache=True, limit=conn_count, conn_timeout=60)
    start(url, force_update, _conn)

    if bundle_env:
        input('Press any key to exit')


if __name__ == '__main__':
    cli()