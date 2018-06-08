#! /usr/bin/env python
# -*- coding: utf-8 -*-

import db
from collections import defaultdict
from extension import mongodb_cli, BulkWriteError
from config import Config

ONLY_DISPLAY = True
SIZE = 1000
BTC_IN_SATOSHIS = 10 ** 8

def run(sid, eid):
    
    while sid < eid:        
        mid = sid + Config.TX_RANGE
        fix_tx_value(sid, mid)
        sid = mid

    
def update_tx_value(tx_value):
    
    addrs = defaultdict(set)
    tx_list = []
    for tx_id in tx_value:
        value_out = tx_value[tx_id]['value_out']
        value_in = tx_value[tx_id]['value_in']
        pubkeys  = tx_value[tx_id]['pubkeys']
        coindd_raw =   tx_value[tx_id]['coindd'] / Config.BTC_IN_SATOSHIS 
        coindd = round(coindd_raw, 2)
        hash = tx_value[tx_id]['tx_hash']


        #print "tx_value", tx_id, value_in, value_out, pubkeys, coindd
        tx_info = {'tx_id': tx_id, 'value_out':value_out,  'value_in': value_in, 
                   'pubkeys': pubkeys, 'coindd':coindd, 'time': 0}
            
        if not Config.DEBUG:
            mongodb_cli.bulk_insert(tx_info)


def fix_tx_value(sid, eid):
        
    inputs = db.get_txin_info_in_range(sid, eid)
    outputs = db.get_txout_info_in_range(sid, eid)

    addr_info = defaultdict(dict)
    tx_value = defaultdict(dict)
    tx_time = defaultdict(int)
    
    for output in outputs:
        # null output
        if  output[0] is None:
            continue
        out_time, tx_id, txout_value, pk_id = int(output[3]), int(output[2]), int(output[1]), int(output[0])
        if not tx_value.get(tx_id):
            tx_value[tx_id] = defaultdict(int)
        tx_value[tx_id]['value_in'] += txout_value
        tx_value[tx_id]['pubkeys'] += 1
        tx_time[tx_id] = out_time 
          
    #analysis inputs
    for input in inputs:
        # coinbase tx
        if input[0]is None:
            continue
        in_time, tx_id, txin_value, pk_id = int(input[3]), int(input[2]), int(input[1]), int(input[0])
        if not tx_value.get(tx_id):
            tx_value[tx_id] = defaultdict(int)
        tx_value[tx_id]['value_out'] += txin_value
        tx_value[tx_id]['pubkeys'] += 1 
        tx_value[tx_id]['coindd'] +=  1.0 * (tx_time[tx_id]-in_time) * txin_value / 86400
    
    #update tx_value
    mongodb_cli.bulk_start(Config.tx_value_db)
    update_tx_value(tx_value)

    try:
        mongodb_cli.bulk_end()
    except BulkWriteError as err:
        print err.details  


    

#run_schedule()
#close_session()    
