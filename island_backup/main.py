import os
import shutil
import sys
import aiohttp
import asyncio
from functools import partial
import urllib.parse as urllib_parse
from island_backup.island_switcher import island_switcher
from .settings import settings
from jinja2 import Environment, FileSystemLoader
import click
from tqdm import tqdm
import logging

from . import network
from .network import get_data
from . import version as __version__
logging.basicConfig(level=logging.INFO, format='{asctime}:{name}:{levelname}: {message}', style='{')

from typing import Optional
import code

##########
# setup
##########


bundle_env = getattr(sys, 'frozen', False)

if bundle_env:
    # pyinstaller attribute, work on windows
    BASE = sys._MEIPASS # type: ignore
    

else:
    BASE = os.path.dirname(__file__)

TEMPLATES_PATH = os.path.join(BASE, 'templates')


env = Environment(loader=FileSystemLoader(TEMPLATES_PATH), trim_blocks=True)
# loop_runner = asyncio.Runner()
# loop_runner.get_loop()



################
# main
################


def template_render(name, **context):
    return env.get_template(name).render(**context)




class ImageManager:
    def __init__(self, image_dir, max_tasks=150, force_update=False):
        self.url_set = set()
        self.sem = asyncio.Semaphore(max_tasks)
        self.busying_url = set()
        self.busying_task = set()
        self.image_dir = image_dir
        self.pdbar = tqdm(desc='image downloading...', position=1)
        # force update image
        self.force_update = force_update


    @staticmethod
    def get_image_name(url):
        path = urllib_parse.urlsplit(url).path
        name = path.split('/')[-1]
        return name

    def get_image_path(self, url):
        file_name = self.get_image_name(url)
        file_path = os.path.join(self.image_dir, file_name)
        return file_path
    
    async def submit(self, url, headers=None):
        task = asyncio.create_task(self._download(url, headers=headers))
        self.busying_task.add(task)
        task.add_done_callback(self.busying_task.discard)

    async def _download(self, url, headers=None):
        if url in self.url_set:
            return
        else:
            self.url_set.add(url)
        logging.debug('prepare download %s', url)
        file_path = self.get_image_path(url)

        if not self.force_update and os.path.exists(file_path):
            return



        data = await get_data(url, as_type='read', headers=headers,)
        await self.save_file(data, file_path=file_path)
        self.sem.release()
        self.status_info()
    

    async def save_file(self, data, file_path):
        content = data
        if not content:
            logging.debug('no data available')
            return

        logging.debug('save file to %s', file_path)

        with open(file_path, 'wb') as f:
            f.write(content)

    async def wait_all_task_done(self):
        # logging.debug('begin waiting')
        # while True:
        #     await asyncio.sleep(3)
        #     if not self.busying_url:
        #         logging.debug('Finish Waitting, all images has been downloaded')
        #         break
        #     logging.debug('Still waitting for all images be downloaded')
        # self.pdbar.close()


        await asyncio.gather(*self.busying_task)

        self.pdbar.close()

    def status_info(self):
        self.pdbar.update()

        logging.debug('this is {} in busying'.format(len(self.busying_url)))
        urls = []
        for i, url in enumerate(self.busying_url):
            if i >= 3:
                break
            urls.append(url)

        logging.debug('urls[3] is %s', urls)


def split_page_write(path, filename, blocks, page_num=50, force_update=False):

    def _cp_static_file(path, force_update):
        static_directory = os.path.join(TEMPLATES_PATH, 'static')
        target_directory = os.path.join(path, 'static')
        # determine whether remove exists path or return
        if os.path.exists(target_directory):
            if force_update:
                shutil.rmtree(target_directory)
            else:
                return
        # copy directory
        shutil.copytree(static_directory, target_directory)

    def write_to_html(path, file_name, all_blocks, page_obj=None):
        thread_id = file_name
        file_name = file_name + '.html'
        save_to = os.path.join(path, file_name)
        with open(save_to, 'w', encoding='utf8') as f:
            f.write(template_render('base.html', title=thread_id, all_blocks=all_blocks, page_obj=page_obj))


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

    _cp_static_file(path, force_update=force_update)


async def main_processor(first_url, image_manager:ImageManager,base_dir=None, folder_name=None,  force_update=False) -> None:
    _tasks = []
    Page = island_switcher.island_page_model
    all_blocks = []
    p = await Page.from_url(first_url, page_num=1)
    process_bar = tqdm(total=p.total_page, position=0, desc='page scanning')
    process_bar.update()
    while True:
        thread_list = p.thread_list()
        for block in thread_list:
            if block.image_url:
                await image_manager.submit(block.image_url, headers=block.headers)
                block.image = 'image/' + image_manager.get_image_name(block.image_url)
                logging.debug('block.image set to -> %s', block.image)

        all_blocks.extend(thread_list)

        if p.has_next():
            p = await Page.from_url(*p.next_page_info)
            process_bar.update()
        else:
            break

    split_page_write(path=base_dir, filename=folder_name, blocks=all_blocks, page_num=50, force_update=force_update)
    process_bar.close()
    await image_manager.wait_all_task_done()



async def start(raw_url, force_update, proxy=None, conn_kwargs={}):
    if proxy:
       network.proxy = proxy
    _conn = aiohttp.TCPConnector(**conn_kwargs)
    network.session = aiohttp.ClientSession(connector=_conn)
    try:
        if proxy:
            logging.info('Test whether proxy config is correct')
            await verify_proxy(proxy)
    except (aiohttp.ClientHttpProxyError, ConnectionRefusedError, AssertionError) as e:
        print('Proxy config is wrong!\n {}'.format(e))
        exit()


    island_switcher.detect_by_url(raw_url)
    sanitized_url = island_switcher.sanitize_url(raw_url)
    folder_name = island_switcher.get_folder_name(raw_url)
    base_dir = os.path.join('backup', folder_name)
    image_dir = os.path.join(base_dir, 'image')
    os.makedirs(image_dir, exist_ok=True)

    logging.info('url is %s', sanitized_url)
    logging.info('island is %s', island_switcher.island)

    image_manager = ImageManager(image_dir, force_update=force_update)
    await main_processor(sanitized_url, base_dir=base_dir, image_manager=image_manager,
                         folder_name=folder_name, force_update=force_update)
    await network.session.close()
  


async def verify_proxy(proxy):
    url = 'https://api.github.com/users/littlezz'
    async with network.session.get(url, proxy=proxy) as r:
        status = r.status
        logging.info('test proxy status, [{}]'.format(status))
        assert r.status == 200


def cli_url_verify(ctx, param, value):
    if value is None:
        return
    if not any(i in value for i in island_switcher.available_island):
        raise click.BadParameter('Unsupported url {}:'.format(value))
    return value



@click.command()
@click.argument('url', required=False, callback=cli_url_verify)
@click.option('-url', prompt='Please Input Url', callback=cli_url_verify)
@click.option('--debug', is_flag=True, help='enable debug mode', default=settings['debug'])
@click.option('--force-update', is_flag=True, help='force update image', default=settings['force-update'])
@click.option('--conn-count', type=click.IntRange(1, 20), default=settings['conn-count'],
              help='max conn number connector use. from 1 to 20. Default is 20')
@click.option('--proxy', '-p', required=False, default=settings['proxy'],
              help='http proxy, ex, http://127.0.0.1:1080')
@click.version_option(version=__version__)
def cli(url, debug, force_update, conn_count, proxy):
    click.echo('version: {}'.format(__version__))

    if debug:
        logging.root.setLevel(logging.DEBUG)
        asyncio.get_event_loop().set_debug(True)

    logging.info('conn number is %s', conn_count)
    logging.info('proxy is %s', proxy)
    logging.info('force-update is %s', force_update)

    logging.debug('settings: {}'.format(settings))
    conn_kwargs = dict(
        use_dns_cache=True,
        limit=conn_count,

    )


    asyncio.run(start(url, force_update,proxy=proxy, conn_kwargs=conn_kwargs))

    if bundle_env:
            click.echo('\n')
            input('Press any key to exit')


if __name__ == '__main__':
    cli()
