import asyncio
import logging
import os
import shutil
import sys


import click
from jinja2 import Environment, FileSystemLoader
from tqdm import tqdm
from island_backup.image_manager import ImageManager

from island_backup.island_switcher import island_switcher

from . import network
from . import version as __version__
from .settings import settings

logging.basicConfig(level=logging.INFO, format='{asctime}:{name}:{levelname}: {message}', style='{')


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

async def dead():
    await network.client.close()
    exit()


async def start(raw_url, force_update, proxy=None, conn_kwargs={}, use_model_name=None, dry_run=False):
    await network.client.init_client(proxy=proxy,conn_kwargs=conn_kwargs)
    if use_model_name:
        island_switcher.specify_island_model(use_model_name)
    else:
        island_switcher.detect_by_url(raw_url)
    sanitized_url = island_switcher.sanitize_url(raw_url)
    folder_name = island_switcher.get_folder_name(raw_url)
    base_dir = os.path.join('backup', folder_name)
    image_dir = os.path.join(base_dir, 'image')
    logging.info('url is %s', sanitized_url)
    logging.info('island is %s', island_switcher.island_model_name)
    if dry_run:
        await dead()
    os.makedirs(image_dir, exist_ok=True)


    image_manager = ImageManager(image_dir, force_update=force_update)
    await main_processor(sanitized_url, base_dir=base_dir, image_manager=image_manager,
                         folder_name=folder_name, force_update=force_update)
    await network.client.close()
  


def cli_url_verify(ctx, param, value):
    if ctx.params.get('dry_run'):
        return value
    if value is None:
        return
    if not any(i in value for i in island_switcher.available_island_url_name):
        raise click.BadParameter('Unsupported url {}:'.format(value))
    return value

def specify_island_model(ctx, param, value):
    if value is None:
        return
    value = value.lower()
    if not any(value==i for i in island_switcher.available_island_model_name):
        raise click.BadParameter('Unknown island model, avaialable model is {}.'.format(', '.join(island_switcher.available_island_model_name)))
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
@click.option('--use', 'use_model', required=False, callback=specify_island_model,default=None,
              help="Select model for url: Nimingban, 2Chan, 4Chan")
@click.option("--dry-run", is_flag=True, default=False, is_eager=True)
@click.version_option(version=__version__)
def cli(url, debug, force_update, conn_count, proxy, use_model, dry_run):
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


    asyncio.run(start(url, force_update,proxy=proxy, conn_kwargs=conn_kwargs,
                       use_model_name=use_model,dry_run=dry_run))

    if bundle_env:
            click.echo('\n')
            input('Press any key to exit')


if __name__ == '__main__':
    cli()
