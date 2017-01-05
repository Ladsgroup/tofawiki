import redis

from .cache import Cache


class RedisCache(Cache):
    def __init__(self, config):
        self.redis = redis.Redis(
            host=config['host'],
            port=config['port']
        )
        self.values = {}

    def get_value(self, key):
        if key not in self.values:
            res = self.redis.get(key)
            if res is not None:
                self.values[key] = res.decode('utf-8')

        return self.values.get(key)

    def write_new_cache(self, key, res):
        # Expires in seven days
        self.redis.set(key, res, ex=7 * 3600 * 24)

    def blow_cache(self):
        # No need to blow
        pass
