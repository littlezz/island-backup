import json
import os.path



SEARCH_PATH = ['.', os.path.expanduser('~/.island_backup')]
CONFIG_FILENAME = 'island_backup.json'


settings = {
    'proxy': None,
    'debug': False,
    'force-update': False,
    'conn-count': 20,
}


def load_config():
    for basepath in SEARCH_PATH:
        filename = os.path.join(basepath, CONFIG_FILENAME)
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf8') as f:
                    user_settings = json.load(f)
            except json.JSONDecodeError:
                print("ERROR: Can not decode {}!\n".format(filename))
            except:
                print('WARNING: Unexcept Error in {}, Ignore.'.format(filename))

            else:
                print('Find island_backup.json at {}'.format(filename))
                return user_settings
    return None


user_settings = load_config()
if user_settings:
    settings.update(user_settings)


