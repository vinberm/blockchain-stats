# -*- coding: utf-8 -*-

import logging
import db
import time
from extension import mongodb_cli,  rc_main as redis_cli
from exception import BulkWriteError
from utils import hashout_hex
from collections import defaultdict
from config import Config

ORPHAN_CUR  = {}

def check_orphan(tx_id, ntime):
    ORPHAN_CUR.setdefault(tx_id, ntime)
    check = True if ORPHAN_CUR[tx_id] != ntime else False
    return check


def update_address_tx(pk_id, tx_set, pk_sent):
    
    tx_list = list(tx_set[pk_id])
    tx_list.sort()
    
    sent_list= [0 if pk_sent[id]>0 else 1 for id in tx_list]
    count = sent_list.count(1)
        
    if not Config.DEBUG:
        res = mongodb_cli.get_last_one(Config.address_tx, {"pubkey_id": pk_id}, "shard")
        shard, size, sent = res['shard'] if res else 0, res['size'] if res else 0, res['sent'] if res else 0 
        if size + len(tx_list) <= Config.SHARDING_SIZE:  
            cond = {"pubkey_id": pk_id, "shard": shard}       
            set_size = {"size": size+len(tx_list), "sent": sent+count}
            mongodb_cli.bulk_push_to_list(cond, {"tx_list": tx_list, "sent_list":sent_list}, set_size)

        else:     
            n =  Config.SHARDING_SIZE - size 
            sc = sent_list[:n].count(1)
            cond = {"pubkey_id": pk_id, "shard": shard} 
            set_size = {"size": Config.SHARDING_SIZE, "sent":sent+sc}
            mongodb_cli.bulk_push_to_list(cond, {"tx_list": tx_list[:n], "sent_list":sent_list[:n]}, set_size)
            
            cond = {"pubkey_id": pk_id, "shard": shard+1} 
            set_size = {"size": len(tx_list)-n, "sent": count-sc}
            mongodb_cli.bulk_push_to_list(cond, {"tx_list": tx_list[n:], "sent_list":sent_list[n:]}, set_size)
   
    
   
def update_tx_value(tx_value):
    
    
    addrs = defaultdict(set)
    tx_list = []
    redis_conn = True if redis_cli.ping() else False
    tx_time = 0
    
    for tx_id in tx_value:
        value_out = tx_value[tx_id]['value_out']
        value_in = tx_value[tx_id]['value_in']
        pubkeys  = tx_value[tx_id]['pubkeys']
        coindd_raw =   tx_value[tx_id]['coindd'] / Config.BTC_IN_SATOSHIS 
        coindd = round(coindd_raw, 2)
        hash = tx_value[tx_id]['tx_hash']
        tx_hash = str(hash).lower()
        tx_time = redis_cli.get_time(tx_hash) if redis_conn else 0        

        tx_info = {'value_out':value_out,  'value_in': value_in, 
                   'pubkeys': pubkeys, 'coindd':coindd, 'time': tx_time}
        
        tx_list.append(tx_info)
    
        if not Config.DEBUG:
            mongodb_cli.bulk_upsert_tx_value(tx_id, tx_info)
            
            
def update_address_info(pk_id, pk_info):

    record = mongodb_cli.get(Config.address_info, {'pubkey_id': pk_id})
    flag = True if record else False
    
    if record:
        flag = True
        bal = record['balance']
        txcounts = record['txcounts']
        txin = record['txin']
        txout = record['txout']
        first_txid = record['first_txid']
        last_sent_txid = record['last_sent_txid']
        last_recv_txid = record['last_recv_txid']
        receive  = record['receive'] if record.get('receive') != None else 0
    else:
        flag = False
        bal = 0
        txcounts = 0
        txin = 0
        txout =  0
        first_txid = pk_info['first_txid']
        last_sent_txid = 0
        last_recv_txid = 0
        receive = 0
    
    pk_info['balance']+= bal
    pk_info['txcounts'] += txcounts
    pk_info['txin'] += txin
    pk_info['txout'] += txout
    pk_info['first_txid'] = first_txid 
    pk_info['last_sent_txid'] = max(pk_info['last_sent_txid'], last_sent_txid)
    pk_info['last_recv_txid'] = max(pk_info['last_recv_txid'], last_recv_txid)
    pk_info['receive'] += receive

    if not Config.DEBUG:
        mongodb_cli.bulk_update_address_info(pk_id, pk_info)


def process_tx(block_id):
    
    tx_ids = db.block_get_tx(block_id) 
    
    if not tx_ids: return
    
    inputs = db.get_txin_info_in_range(tx_ids)
    outputs = db.get_txout_info_in_range(tx_ids)

    addr_info = defaultdict(dict)
    tx_value = defaultdict(dict)
    tx_set = defaultdict(set)
    tx_time = defaultdict(int)
    sent_set = defaultdict(dict)    
    
    for output in outputs:
        # null output
        if  output[0] is None:
            continue
        
        tx_hash, out_time, tx_id, txout_value, pk_id =output[4], int(output[3]), int(output[2]), int(output[1]), int(output[0])
                
        if check_orphan(tx_id, out_time):
            continue

        if not addr_info.get(pk_id):
            addr_info[pk_id] = defaultdict(int)
            addr_info[pk_id]['first_txid'] = tx_id
        
        addr_info[pk_id]['balance'] +=txout_value
        addr_info[pk_id]['txin'] += 1
        addr_info[pk_id]['receive'] += txout_value
        addr_info[pk_id]['last_recv_txid'] = max(addr_info[pk_id]['last_recv_txid'], tx_id)
        addr_info[pk_id]['first_txid'] = min(addr_info[pk_id]['first_txid'], tx_id)
        
        if not tx_value.get(tx_id):
            tx_value[tx_id] = defaultdict(int)
        tx_value[tx_id]['value_in'] += txout_value
        tx_value[tx_id]['pubkeys'] += 1
        tx_value[tx_id]['tx_hash'] = tx_hash
        tx_time[tx_id] = out_time 
        tx_set[pk_id].add(tx_id)

        if not sent_set.get(pk_id):
            sent_set[pk_id] = defaultdict(int)
        sent_set[pk_id][tx_id] += txout_value
        
        
    #analysis inputs
    for input in inputs:
        # coinbase tx
        if input[0]is None:
            continue
        
        tx_hash, in_time, tx_id, txin_value, pk_id = input[4], int(input[3]), int(input[2]), int(input[1]), int(input[0])
        if check_orphan(tx_id, in_time):
            continue

        if not addr_info.get(pk_id):
            addr_info[pk_id] = defaultdict(int)
            addr_info[pk_id]['first_txid'] = tx_id

        addr_info[pk_id]['balance'] -= txin_value
        addr_info[pk_id]['txout'] += 1
        addr_info[pk_id]['sent'] += txin_value
        addr_info[pk_id]['last_sent_txid'] = max(addr_info[pk_id]['last_sent_txid'], tx_id)
        addr_info[pk_id]['first_txid'] = min(addr_info[pk_id]['first_txid'], tx_id)

        
        if not tx_value.get(tx_id):
            tx_value[tx_id] = defaultdict(int)
        tx_value[tx_id]['value_out'] += txin_value
        tx_value[tx_id]['pubkeys'] += 1 
        tx_value[tx_id]['coindd'] +=  1.0 * (tx_time[tx_id]-in_time) * txin_value / 86400
        tx_set[pk_id].add(tx_id)

        if not sent_set.get(pk_id):
            sent_set[pk_id] = defaultdict(int)
        sent_set[pk_id][tx_id] -= txin_value
    
    
    mongodb_cli.bulk_start(Config.address_info)
    # upsert addressinfo,  update addresstx
    prev_val = defaultdict(int)    
    for pk_id in addr_info:
        addr_info[pk_id]['txcounts'] = len(tx_set[pk_id])
        update_address_info(pk_id, addr_info[pk_id])
    try:
        mongodb_cli.bulk_end()
    except BulkWriteError as err:
        print err.details  

    mongodb_cli.bulk_start(Config.address_tx)

    for pk_id in addr_info:
        update_address_tx(pk_id, tx_set, sent_set[pk_id])
    try:
        mongodb_cli.bulk_end()
    except BulkWriteError as err:
        print err.details  

    mongodb_cli.bulk_start(Config.tx_value)
    #update tx_value
    update_tx_value(tx_value)
    try:
        mongodb_cli.bulk_end()
    except BulkWriteError as err:
        print err.details  
