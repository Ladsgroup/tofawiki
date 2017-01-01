import json
import logging

from .cache import Cache


class FileCache(Cache):
    def __init__(self, path='/srv/tofawiki/cache/cache.json'):
        self.values = {}
        self.path = path

    def get_value(self, key):
        if key not in self.values:
            res = self.get_value_from_file(key)
            if res is not None:
                logger = logging.getLogger(__name__)
                logger.debug('Got a key from cache')
                self.values[key] = res

        return self.values.get(key)

    def get_value_from_file(self, key):
        return json.load(open(self.path)).get(key)

    def write_new_cache(self, key, res):
        # TODO: Flush them altogether not one at a time.
        cache = json.load(open(self.path))
        cache[key] = res
        json.dump(cache, open(self.path, 'w'), ensure_ascii=False)

    def blow_cache(self):
        with open(self.path, 'w') as f:
            f.write('{}')
