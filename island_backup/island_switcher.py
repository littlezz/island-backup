from .islands.adnmb import AdnmbPage


island_class_map = {
    'adnmb': AdnmbPage,

}

class IslandSwitcher:
    available_island = island_class_map.keys()

    def __init__(self, island=None):
        self.island = island

    def detect_by_url(self, url):
        for island in self.available_island:
            if island in url:
                self.island = island
                return
        raise ValueError('Unknown url: {}'.format(url))

    @property
    def island_page_model(self):
        return island_class_map[self.island]

    # @property
    # def cdn_host(self):
    #     return _island_info[self.island]['CDNHOST']
    #
    # @property
    # def headers(self):
    #     return _island_info[self.island]['headers']


island_switcher = IslandSwitcher()