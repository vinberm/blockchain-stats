# -*- coding: utf-8 -*-

from db.mongo import MongodbClient
from tools import flags

FLAGS = flags.FLAGS


class DbProxy(object):

    def __init__(self):
        self.mongo_cli = MongodbClient(host=FLAGS.mongo_bytom_host, port=FLAGS.mongo_bytom_port)
        self.mongo_cli.use_db(flags.FLAGS.mongo_bytom)

    def get_recent_height(self):
        state = self.mongo_cli.get(flags.FLAGS.db_status)
        return None if state is None else state[flags.FLAGS.block_height]

    # TODO 索引
    def get_block_by_height(self, height):
        return self.mongo_cli.get_one(flags.FLAGS.block_info, {'height': height})

    def get_status(self):
        state = self.mongo_cli.get_one(
                table=FLAGS.chain_status, cond={
                    FLAGS.block_height: 0})
        return None if state is None else state

    def save_chain(self, status):
        self.mongo_cli.insert(flags.FLAGS.node_status, status)

    def save_chain_patch(self, status_list):
        self.mongo_cli.insert_many(flags.FLAGS.chain_status, status_list)
