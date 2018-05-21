# coding=utf-8

from pymongo import MongoClient
from tools import flags

FLAGS = flags.FLAGS


class MongodbClient:
    def __init__(self, host, port):
        self.conn = MongoClient(host, port, maxPoolSize=300)

    def use_db(self, db_name, mongo_user=None, mongodb_password=None):
        db = self.conn[db_name]
        # to do: add authentication

        # self._auth(db, mongo_user, mongodb_password)
        self.mc = db

    def _auth(self, db, mongo_user, mongodb_password):
        if not mongo_user and not mongodb_password:
            res = db.authenticate(FLAGS.mongodb_user, FLAGS.mongodb_password)
        else:
            res = db.authenticate(mongo_user, mongodb_password)
        if not res:
            raise Exception("Mongodb Authentication Fail")

    def get(self, table, cond=None):
        res = self.mc[table].find_one(cond)
        return res if res else None

    def insert(self, table, value):
        self.mc[table].insert(value)

    def get_all(self, table, cond={}, items=None, n=0, sort_key=None, ascend=True, skip=0):
        collection = self.mc[table].find(cond, items) if items else self.mc[table].find(cond)
        if n > 0:
            if sort_key is not None:
                return collection.limit(n).skip(skip).sort([(sort_key, 1 if ascend else -1)])
            else:
                return collection.limit(n).skip(skip)
        else:
            return collection

    def get_last_n(self, table, args, order, n):
        res = self.mc[table].find(args).sort(order, -1).limit(n)
        return res if res else None

    def get_one(self, table, cond):
        res = self.mc[table].find_one(cond)
        return res if res else None

    def get_many(self, table, cond={}, items=None, n=0, sort_key=None, ascend=True, skip=0):
        collection = self.mc[table].find(cond, items) if items else self.mc[table].find(cond)
        if sort_key:
            n = FLAGS.table_capacity if not n else n
            res = collection.limit(n).skip(skip).sort([(sort_key, 1 if ascend else -1)])
            return list(res) if res else None
        else:
            ''' slice without sort make no sense '''
            res = collection.limit(n).skip(skip)
            return list(res) if res else None

    def insert_one(self, table, value):
        self.mc[table].insert(value)

    def update_one(self, table, cond, operation, upsert):
        self.mc[table].update_one(cond, operation, upsert)

    def update_many(self, table, cond, operation, upsert):
        self.mc[table].update_many(cond, operation, upsert)

    def delete_one(self, table, cond):
        self.mc[table].delete_one(cond)

    def delete_many(self, table, cond):
        self.mc[table].delete_many(cond)

    def count(self, table):
        res = self.mc[table].find().count()
        return int(res) if res else 0

    def count_with_cond(self, table, cond):
        res = self.mc[table].find(cond).count()
        return int(res) if res else 0
