#! /usr/bin/env python
# -*- coding: utf-8 -*-
from extension import rc_main as redis_client

class TxMessage(object):
    
    def __init__(self):
        self.rec_tx = None
        self.cache = redis_client

    def sub_process(self, cmd, data):
        txinfo = {}
        try:
            cur_tx = self.cache.get("CURRENT_TX")
            tx_num = self.cache.get("TX_MEMPOOL_NUM")
            avg_size = self.cache.get("TX_MEMPOOL_SIZE")/int(tx_num) if int(tx_num) !=0 else 0 
            
            print "rec_tx", self.rec_tx
            if not cur_tx:
                print "No Current Tx"
            
            txinfo = {"hash":cur_tx['hash'], 
                      "amount":cur_tx['amount'], 
                      "time": cur_tx['time'], 
                      "tx_num": tx_num, 
                      "avg_size": avg_size}
            
            if cur_tx != self.rec_tx:
                self.rec_tx = cur_tx 
                return txinfo
            else:
                return None
            
        except Exception, e:
            print str(e) 
            return None
        
        