from .islands.bases import BasePage
from .islands.nimingban import NiMingBanPage
from .islands.the2chan import The2ChanPage
from .islands.the4chan import The4ChanPage
from collections import namedtuple

IslandModel = namedtuple('IslandModel', ['model', 'name', 'url_index'])


island_model_index = (
    IslandModel(model=NiMingBanPage, name='nimingban', url_index='nmbxd1'),
    IslandModel(model=The4ChanPage, name='4chan', url_index='4chan'),
    IslandModel(model=The2ChanPage, name='2chan', url_index='2chan'),
)


class IslandSwitcher:
    available_island_url_name = [i.url_index for i in island_model_index]
    available_island_model_name = [i.name for i in island_model_index]

    def __init__(self):
        self._island_model:IslandModel = None
        self._specify_model_flag:bool = False

    def detect_by_url(self, url):
        # specify model by cli option
        if self._specify_model_flag is True:
            return 
        
        for model in island_model_index:
            if model.url_index in url:
                self._island_model = model
                return
            
        raise ValueError('Unknown url: {}'.format(url))
    
    def specify_island_model(self, model_name:str) -> bool:
        model_name = model_name.lower()
        for island_model in island_model_index:
            if model_name == island_model.name:
                self._island_model = island_model
                self._specify_model_flag = True
                return True
        else:
            return False
    
            
    @property
    def island_model_name(self)->str:
        # Prefer user-defined model name
        if self._specify_model_flag:
            return self._island_model.name
        
        if self._island_model is not None:
            return self._island_model.url_index
        else:
            raise

    @property
    def island_page_model(self) -> BasePage:
        return self._island_model.model

    def sanitize_url(self, url):
        return self.island_page_model.sanitize_url(url)

    def get_folder_name(self, url):
        return self.island_model_name + '_' + str(self.island_page_model.get_thread_id(url))


island_switcher = IslandSwitcher()