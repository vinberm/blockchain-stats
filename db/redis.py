import redis


class RedisClient:
    def __init__(self, db):
        pool = redis.ConnectionPool(host=FLAGS.redis_host, port=FLAGS.redis_port, db=db, password=FLAGS.redis_passwd)
        self.rc = redis.Redis(connection_pool=pool)

    def ping(self):
        try:
            self.rc.ping()
            return True
        except Exception, e:
            return False

    def is_set_ttl(self, key):
        res = self.rc.ttl(key)
        return res if res > 0 else False

    def set_expire(self, key, exp_time):
        if not self.is_set_ttl(key):
            self.rc.expire(key, exp_time)

    def exists(self, key):
        return self.rc.exists(key)

    def get(self, key):
        value = self.rc.get(key)
        return eval(value) if value else None

    def set(self, key, value, expire=0):
        str_value = json.dumps(value, ensure_ascii=False)
        self.rc.set(key, value)
        if expire > 0 and not self.is_set_ttl(key):
            self.rc.expire(key, expire)

    def delete(self, key):
        self.rc.delete(key)

    def delete_list(self, keys):
        self.rc.delete(*keys)

    def keys(self, pattern):
        return self.rc.keys(pattern)

    def incr(self, key):
        self.rc.incr(key)

    def incrby(self, key, value):
        self.rc.incrby(key, int(value))

    def decrby(self, key, value):
        self.rc.decr(key, int(value))

    def add(self, key, value):
        self.rc.sadd(key, value)

    def add_list(self, key, value):
        self.rc.sadd(key, *value)

    def len(self, key):
        return self.rc.scard(key)

    def get_list(self, key):
        res = self.rc.smembers(key)
        return list(res) if res else []

    def remove(self, key, value):
        self.rc.srem(key, value)

    def remove_list(self, key, value):
        self.rc.srem(key, *value)

    def hashexist(self, key, field):
        return self.rc.hexists(key, field)

    def hashlen(self, key):
        return self.rc.hlen(key)

    def hashkeys(self, key):
        res = self.rc.hkeys(key)
        return list(res) if res else []

    def hashset(self, key, value):
        self.rc.hmset(key, value)

    def hashget(self, key, field):
        res = self.rc.hget(key, field)
        return eval(res) if res else {}

    def hashget_all(self, key):
        res = self.rc.hgetall(key)
        return res

    def hashdel(self, key, field):
        self.rc.hdel(key, field)

    def hashdel_list(self, key, field):
        self.rc.hdel(key, *field)

    def hash_pop(self, key, field):
        res = self.rc.hget(key ,field)
        self.rc.delete(key)
        return eval(res) if res else {}

    def hash_incrby(self, key, field, value):
        value = self.rc.hincrby(key, field, int(value))
        if value == 0:
            self.hashdel(key, field)

    def add_if_no_exist(self, key, value, expire=0):
        res = self.rc.sadd(key, value)
        if expire > 0 and not self.is_set_ttl(key):
            self.rc.expire(key, expire)
        return True if res > 0 else False

    def set_time(self, field, value):
        self.rc.hsetnx("TX_TIME", field, value)

    def get_time(self, field):
        res = self.rc.hget("TX_TIME", field)
        if res:
            self.rc.hdel("TX_TIME", field)
            return eval(res)
        else:
            return 0
