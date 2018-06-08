import redis
import json
from config import Config

class RedisClient:
    def __init__(self):
        pool = redis.ConnectionPool(host=Config.redis_host, port=Config.redis_port, db=Config.redis_db, password=Config.redis_passwd)
        self.rc = redis.Redis(connection_pool=pool)
        
    def get(self, key):
        value = self.rc.get(key)
        return eval(value) if value else None
    
    def set(self, key, value):
        str_value = json.dumps(value, ensure_ascii=False)
        self.rc.set(key, value)
    
    def delete(self, key):
        self.rc.delete(key)
    
    def incr(self, key):
        self.rc.incr(key)
        
    def incrby(self, key, value):
        self.rc.incrby(key, int(value))
        
    def add(self, key, value):
        self.rc.sadd(key, value) 
        
    def remove(self, key, value):
        self.rc.srem(key, value)
        
    def hashset(self, key, value):
        self.rc.hmset(key, value)

redis_cli = RedisClient()
