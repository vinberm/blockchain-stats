#! /usr/bin/env python
# -*- coding: utf-8 -*-
import time
import flags
from ast import literal_eval
from extension import  rc_main, rc_probe
from collections import defaultdict

FLAGS = flags.FLAGS

class BlockProc():
    def __init__(self):
        self.rc_m = rc_main
        self.rc_p = rc_probe
        self.expire = 21600
        
                
    def notify(self, block):
    
        block_info = literal_eval(block)
        now = int(time.time())
        
        block_tx = [tx['hash'] for tx in block_info['txs']] 

        stale_tx =[]
        stale_tx.extend(block_tx)
        
        #stale tx
        txs = self.rc_m.hashget_all("TX_MEMPOOL")
        for hash, t in txs.items():
            if now - int(t) > self.expire:
                stale_tx.append(hash)
        
        print "STALE_TX_NUM: %d" % len(stale_tx)
        self._clear_mempool(set(stale_tx))
                

    def _clear_mempool(self, txs):
        
        addrs = defaultdict(set)
        tx_hashs = []
        keys = []
        for tx_hash in txs:
            #tx_hash = tx['hash']
            
            tx_hashs.append(tx_hash)
            keys.append("UNCONFIRMED_%s" % tx_hash)
            tx_info = self.rc_m.hashget("UNCONFIRMED_%s" % tx_hash, 'detail')
            
            for input in tx_info.get('inputs', ()):
                if type(input['addr']) == list: 
                    for addr in input['addr']:
                        addrs[addr].add(tx_hash)
                else:
                    addrs[input['addr']].add(tx_hash)
            for output in tx_info.get('outputs', ()):
                if type(output['addr']) == list: 
                    for addr in output['addr']:
                        addrs[addr].add(tx_hash)
                else:
                    addrs[output['addr']].add(tx_hash)
            
            size = tx_info.get('size', 0)
            if size > 0:
                self.rc_m.decrby("TX_MEMPOOL_SIZE", size)
            
            #conflict
            #for v in tx['vin']:
                #self.rc_p.delete("UTXO_%s_%d" % (v['prev_output'],int(v['pos'])))
        
        #remove ADDR
        for addr, tx_list in addrs.items():
            self.rc_m.remove_list("ADDR_%s" % addr, list(tx_list))
        
        #remove TX_MEMPOOL
        self.rc_m.hashdel_list("TX_MEMPOOL" , tx_hashs)
        self.rc_m.delete_list(keys)
        print "STALE_TX: %s" % str(keys)
         
       
       