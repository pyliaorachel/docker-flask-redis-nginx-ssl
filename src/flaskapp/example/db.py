import os

import redis


class Database:
    def __init__(self):
        redis_host = os.environ.get('REDIS_HOST', '127.0.0.1')
        redis_port = os.environ.get('REDIS_PORT', 6379)

        self.db = redis.StrictRedis(host=redis_host, port=redis_port)

    def set(self, key, value):
        self.db.set(key, value)

    def get(self, key):
        value = self.db.get(key)
        return None if not value else value.decode('utf-8')
