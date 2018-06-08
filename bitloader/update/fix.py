#! /usr/bin/env python
# -*- coding: utf-8 -*-
import db
from config import Config
from extension import mongodb_cli
from collections import defaultdict


def fix_address_info(pk_id, addr):
    
    record = mongodb_cli.get(Config.address_info, {'pubkey_id': pk_id})
    if record: 
        record['balance'] -= addr['balance']
        record['receive'] -= addr['receive']        
        if not Config.DEBUG:
            mongodb_cli.bulk_update_address_info(pk_id, record)


def fix_orphan():
    
    orphans = db.find_orphan()
    rec = mongodb_cli.get_checkpoint(Config.checkpoint, 'orphan_blocks')
    
    if orphans == rec: return 
    
    orphan_ids = orphans[:orphans.index(rec[0])]
    addr_info = defaultdict(dict)

    inputs = db.get_txin_info_by_blocks(orphan_ids) 
    outputs = db.get_txout_info_by_blocks(orphan_ids)
        
    for output in outputs:
        # null output
        if  output[0] is None:
            continue
        txout_value, pk_id =  int(output[1]), int(output[0])
        if not addr_info.get(pk_id):
            addr_info[pk_id] = defaultdict(int)
        
        addr_info[pk_id]['balance'] += txout_value
        addr_info[pk_id]['receive'] += txout_value
        
    for input in inputs:
        # coinbase tx
        if input[0]is None:
            continue    
        txin_value, pk_id =  int(input[1]), int(input[0])
        if not addr_info.get(pk_id):
            addr_info[pk_id] = defaultdict(int)

        addr_info[pk_id]['balance'] -= txin_value
        addr_info[pk_id]['sent'] += txin_value
    
    mongodb_cli.bulk_start(Config.address_info_db)
    
    for pk_id, addr in addr_info.items():
        fix_address_info(pk_id, addr)
    try:
        mongodb_cli.bulk_end()
    except BulkWriteError as err:
        print err.details  