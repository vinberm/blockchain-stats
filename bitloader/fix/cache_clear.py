#! /usr/bin/env python
# -*- coding: utf-8 -*-

import time
from utils import ONE_DAY
from extension import rc_main, rc_probe

def run_schedule():
    now = int(time.time())
    clear_stale_tx(now)
    clear_stale_conflict(now)

def clear_stale_tx(now):
    
    for key in rc_main.keys('UNCONFIRMED_*'):
        tx = rc_main.hashget(key, 'detail')
        
        addrs = set()
        if tx['tx_time'] + ONE_DAY < now:
            for input in tx['inputs']:
                addrs.add(input['addr'])
            for output in tx['outputs']:
                addr = output['addr']
                if type(addr) == str and addr != 'Unknown':
                    addrs.add(addr)
                if type(addr) == list:
                    for i in addr:
                        addrs.add(i)
                        
            #UNCONFIRMED_Hash 更新
            rc_main.delete(key)
            
            #ADDR cache 更新
            tx_hash, tx_size = tx['hash'], tx['size']
            for addr in addrs:
                rc_main.remove("ADDR_%s" % addr,  tx_hash)
                
            #减少TX_MEMPOOL 统计               
            rc_main.remove("TX_MEMPOOL",  tx_hash)
            rc_main.decrby("TX_MEMPOOL_SIZE", tx_size)


def clear_stale_conflict(now):
    rc_probe.delete('CONFLICT_TXS')


if __name__ == '__main__':
    run_schedule()
