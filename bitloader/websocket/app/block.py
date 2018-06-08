#! /usr/bin/env python
# -*- coding: utf-8 -*-
from extension import rc_main as redis_client


class BlockMessage(object):
    
    def __init__(self):
        self.rec_height = None
        self.cache = redis_client

    def sub_process(self, cmd, data):
        
        blockinfo = {}
        try:
            cur_block = self.cache.get("CURRENT_BLOCK")
            if self.rec_height < cur_block['height']: 
                self.rec_height = cur_block['height']
                return cur_block
            else:
                return None
        except Exception, e:
            print str(e)
            return None 
        
        
