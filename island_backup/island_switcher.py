from .islands.nimingban import NiMingBanPage
from .islands.the4chan import The4ChanPage
from .islands.the2chan import The2ChanPage
from .islands.bases import BasePage


island_class_map = {
    'nmbxd1': NiMingBanPage,
    '4chan': The4ChanPage,
    '2chan': The2ChanPage,
}

class IslandSwitcher:
    available_island = island_class_map.keys()

    def __init__(self):
        self._island:str|None = None

    def detect_by_url(self, url):
        for island in self.available_island:
            if island in url:
                self._island = island
                return
        raise ValueError('Unknown url: {}'.format(url))
    
    @property
    def island(self)->str:
        if self._island is not None:
            return self._island
        else:
            raise

    @property
    def island_page_model(self) -> BasePage:
        return island_class_map[self.island]

    def sanitize_url(self, url):
        return self.island_page_model.sanitize_url(url)

    def get_folder_name(self, url):
        return self.island + '_' + str(self.island_page_model.get_thread_id(url))


island_switcher = IslandSwitcher()