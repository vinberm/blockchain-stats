#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys
path = os.path.abspath(os.path.join(os.path.dirname('.'),os.path.pardir))
sys.path.append(path)

import logging
import util, log, BCDataStream 
from Datastore import DataStore
from config import Config

from extension import rpc_client, redis_client
from exception import LoadError

LOG = logging.getLogger('ChainLoader')


class ChainLoader:

    def __init__(self):
       self.store = DataStore(10000)
       self.cache = redis_client
       self.rpc = rpc_client
       self.chain = None


    def process(self):
        try:
            if not self.catch_up():
                LOG.debug("catch_up: abort")        
            self.store.flush()
        except Exception, e:
            LOG.error("Failed to catch up %s" % str(e))
            self.store.rollback()
            
    def catch_up(self):

        chain_name = Config.chain
        if chain_name is None:
            LOG.error("No Chain Found")
            return False
        
        chain = self.store.chains_by.name[chain_name]
                                
        try:
            cur_height = self.store.get_block_number()+1
            
            bc = self.rpc.getblockchaininfo()
            nxt_height = bc['blocks']
            
            while cur_height <= nxt_height:
                
                hash = self.rpc.getblockhash(cur_height)     
                block_hex = self.rpc.getblock(hash, False)
                raw = self.store.binin_hex(block_hex)
                self.load_binary(chain, raw)
                cur_height += 1           
        except LoadError, e: 
             LOG.error('Something Wrong')   

                  
    def load_binary(self, chain, raw):
        
        ds = BCDataStream.BCDataStream(raw, 0)
        
        block_size = len(ds.input)
        
        end = ds.read_cursor + block_size
        hash = chain.ds_block_header_hash(ds)

        if not self.store.offer_existing_block(hash, chain.id):
            b = chain.ds_parse_block(ds)
            b["hash"] = hash

            if  b["hashPrev"] == chain.genesis_hash_prev:
                try:
                    LOG.debug("Bitcoin genesis tx: %s", b['transactions'][0]['__data__'].encode('hex'))
                except Exception:
                    pass
            
            self.store.import_block(b, chain = chain)
            if ds.read_cursor != end:
                LOG.debug("Skipped %d bytes at block end",end-ds.read_cursor)
                
            ds.read_cursor = end
            self.store.bytes_since_commit += block_size
            if self.store.bytes_since_commit >= store.commit_bytes:
                self.store.flush()






if __name__ in "__main__":
    abe = ChainLoader()
    abe.process()      