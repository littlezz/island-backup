import asyncio
import logging
import os
import urllib.parse

from tqdm import tqdm

from . import network


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
        path = urllib.parse.urlsplit(url).path
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



        data = await network.client.get_data(url, as_type='read', headers=headers,)
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