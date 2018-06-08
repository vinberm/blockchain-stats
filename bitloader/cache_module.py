import redis
import flags
import json
from pymongo import MongoClient
from geoip2 import database
from geoip2.errors import AddressNotFoundError 
from decorators import slice

FLAGS = flags.FLAGS


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
        


class MongodbClient:
    def __init__(self):
        self.conn = MongoClient(FLAGS.mongodb_host, FLAGS.mongodb_port, maxPoolSize=300)
        self.pipe = None
    
    def use_db(self, db_name):
        db = self.conn[db_name]
        self._auth(db)
        self.mc = db
    
    def _auth(self, db):
        res = db.authenticate(FLAGS.mongodb_user, FLAGS.mongodb_password)
        if not res:
            raise Exception("Mongodb Authentication Fail")
    
    def close(self):
        self.conn.close()
    
    def bulk_start(self, table):
        self.pipe = self.mc[table].initialize_unordered_bulk_op()
    
    def bulk_end(self):
        if self.pipe:
            self.pipe.execute()
    
    def bulk_insert(self, value):
        self.pipe.insert(value)
    
    def bulk_upsert_tx_value(self, tx_id, args):
        self.pipe.find({'tx_id': tx_id}).upsert().update({"$set":args})
    
    def bulk_update_address_info(self, pk_id, args):
        self.pipe.find({'pubkey_id': pk_id}).upsert().update({"$set":args})
    
    def bulk_push_to_list(self, cond, push_list, setting):
        self.pipe.find(cond).upsert().update({"$pushAll": push_list, "$set":setting})
    
    #@slice
    def get(self, table, args):
        return self.mc[table].find_one(args)
    
    def insert(self, table, id, value):
        self.mc[table].insert(value)
    
    def insert_many(self, table, rec_list):        
        self.mc[table].insert_many(rec_list)

    def get_checkpoint(self, table, type):
        res = self.mc[table].find_one({'type': type})
        return res['stat'] if res else None
    
    def update_checkpoint(self, table, type, stat):
        self.mc[table].update({'type': type}, {"$set":{'stat': stat}}, upsert=True)
    
    #@slice   
    def get_last_one(self, table, args, order):
        res = self.mc[table].find(args).sort(order, -1).limit(1)
        rlist = list(res)  
        return rlist[0] if rlist else None
    
    #@slice
    def push_to_list(self, table, cond, push_list, setting):
        self.mc[table].update(cond, {"$pushAll": push_list, "$set":setting}, upsert=True)
    
    #@slice
    def update(self, table, query, args):
        self.mc[table].update(query, {"$set":args}, upsert=True)








class GetIpInfo(object):
    def __init__(self, path):
        try:
            self.reader = database.Reader(path)
        except IOError:
            self.reader = None

    def get_country(self, ip):
        try:
            address_info = self.reader.city(ip)
            return address_info.country.iso_code
        except (AddressNotFoundError, ValueError):
            return None
