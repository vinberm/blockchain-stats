#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import time
import logging

import Chain

import BCDataStream
import deserialize
import util
import base58
import db
from exception import DBException

LOG = logging.getLogger('DataStore')


WORK_BITS = 304  # XXX more than necessary.

NULL_PUBKEY_HASH = "\0" * Chain.PUBKEY_HASH_LENGTH
NULL_PUBKEY_ID = 0
PUBKEY_ID_NETWORK_FEE = NULL_PUBKEY_ID

# Size of the script and pubkey columns in bytes.
MAX_SCRIPT = 1000000
MAX_PUBKEY = 65

SCRIPT_ADDRESS_RE = re.compile("\x76\xa9\x14(.{20})\x88\xac\x61?\\Z", re.DOTALL)
SCRIPT_PUBKEY_RE = re.compile(
    ".((?<=\x41)(?:.{65})|(?<=\x21)(?:.{33}))\xac\\Z", re.DOTALL)
SCRIPT_NETWORK_FEE = '\x6a'

class DataStore(object):

    def __init__(store, bytes):
        store.db = db
        store.commit_bytes = bytes  #default bytes
        store.bytes_since_commit = 0
        store._blocks = {}
        store.init_binfuncs()
        store.init_chains()

    def init_chains(store):
        
        store.chains_by = lambda: 0
        store.chains_by.id = {}
        store.chains_by.name = {}
        store.chains_by.magic = {}
        
        chains = store.db.chain_get_all()
        
        for chain_id, magic, chain_name, chain_code3, address_version, script_addr_vers, \
                chain_policy, chain_decimals in chains:
            
            chain = Chain.create(
                id              = int(chain_id),
                magic           = store.binout(magic),
                name            = unicode(chain_name),
                code3           = chain_code3 and unicode(chain_code3),
                address_version = store.binout(address_version),
                script_addr_vers = store.binout(script_addr_vers),
                policy          = unicode(chain_policy),
                decimals        = None if chain_decimals is None else int(chain_decimals))

            store.chains_by.id[chain.id] = chain
            store.chains_by.name[chain.name] = chain
            store.chains_by.magic[bytes(chain.magic)] = chain
    
    
    def import_block(store, b, chain=None):

        tx_hash_array = []
        all_txins_linked = True
        
        b['value_in'] = 0
        b['value_out'] = 0
        b['value_destroyed'] = 0


        # 写入交易数据 获得value_in, value_out, value_destroyed
        for pos in xrange(len(b['transactions'])):
            tx = b['transactions'][pos]

            if 'hash' not in tx:
                tx['hash'] = chain.transaction_hash(tx['__data__'])

            tx_hash_array.append(tx['hash'])
            tx['tx_id'] = store.db.tx_find_id_and_value(tx, pos == 0)

            if tx['tx_id']:
                all_txins_linked = False
            else:
                tx['tx_id'] = store.import_tx(tx, pos == 0, chain)
                if tx.get('unlinked_count', 1) > 0:
                    all_txins_linked = False

            if tx['value_in'] is None:
                b['value_in'] = None
            elif b['value_in'] is not None:
                b['value_in'] += tx['value_in']
            b['value_out'] += tx['value_out']
            b['value_destroyed'] += tx['value_destroyed']


        # block 表中写入数据
        block_id = int(store.new_id("block"))
        b['block_id'] = block_id

        if b['hashMerkleRoot'] != chain.merkle_root(tx_hash_array):
            raise MerkleRootMismatch(b['hash'], tx_hash_array)

        #寻找父节点
        hashPrev = b['hashPrev']
        is_genesis = hashPrev == chain.genesis_hash_prev

        (prev_block_id, prev_height, prev_work, prev_satoshis,
         prev_seconds, prev_ss, prev_total_ss, prev_nTime) = (
            (None, -1, 0, 0, 0, 0, 0, b['nTime'])
            if is_genesis else
            store.db.find_prev(store.hashin(hashPrev)))

        b['prev_block_id'] = prev_block_id
        b['height'] = None if prev_height is None else prev_height + 1
        b['chain_work'] = util.calculate_work(store.binout_int(prev_work), b['nBits'])

        b['seconds'] = None if prev_seconds is None else (prev_seconds+b['nTime']-prev_nTime)
       
        if prev_satoshis is None or prev_satoshis < 0 or b['value_in'] is None:
            b['satoshis'] = -1-b['value_destroyed']
        else:
            b['satoshis'] = prev_satoshis+b['value_out']-b['value_in']-b['value_destroyed']

        if prev_satoshis is None or prev_satoshis < 0:
            ss_created = None
            b['total_ss'] = None
        else:
            ss_created = prev_satoshis * (b['nTime'] - prev_nTime)
            b['total_ss'] = prev_total_ss + ss_created

        if b['height'] is None or b['height'] < 2:
            b['search_block_id'] = None
        else:
            b['search_block_id'] = store.get_block_id_at_height(
                util.get_search_height(int(b['height'])),
                None if prev_block_id is None else int(prev_block_id))

        # Insert the block table row.
        try:
            bk = {"block_id" : block_id,
                  "height": b['height'],
                  "bhash": store.hashin(b['hash']),
                  "ntime": store.intin(b['nTime']),
                  "mroot": store.hashin(b['hashMerkleRoot']),
                  "version":  store.intin(b['version']),
                  "height": b['height'],
                  "prev_block_id": prev_block_id,
                  "chain_work": store.binin_int(b['chain_work'], WORK_BITS),
                  "nbits": store.intin(b['nBits']),
                  "nonce": store.intin(b['nNonce']),
                  "value_in": store.intin(b['value_in']),
                  "value_out": store.intin(b['value_out']),
                  "satoshis": store.intin(b['satoshis']),
                  "seconds": store.intin(b['seconds']),
                  "total_ss": store.intin(b['total_ss']),
                  "txs":   len(b['transactions']), 
                  "search_id": b['search_block_id']
                  }
            store.db.insert_block(bk)
            
        except DBException:
            #异常出错
            raise

        # block_tx 表中写入数据
        for tx_pos in xrange(len(b['transactions'])):
            tx = b['transactions'][tx_pos]
            store.db.insert_block_tx(block_id, tx, tx_pos)
            LOG.info("block_tx %d %d", block_id, tx['tx_id'])


        # block 表和block_txin 其他项写入
        if b['height'] is not None:
            store.populate_block_txin(block_id)
            if all_txins_linked or store.db.get_unlinked_txins(block_id) <= 0:
                b['ss_destroyed'] = store.db.get_block_ss_destroyed(
                    block_id, b['nTime'],
                    map(lambda tx: tx['tx_id'], b['transactions']))
                if ss_created is None or prev_ss is None:
                    b['ss'] = None
                else:
                    b['ss'] = prev_ss + ss_created - b['ss_destroyed']
                store.db.update_new_block(store.intin(b['ss']),store.intin(b['ss_destroyed']),block_id)               
            else:
                b['ss_destroyed'] = None
                b['ss'] = None

        
        # 写入block_next 或写入 orphan_block
        if prev_block_id:
            store.db.insert_block_next(prev_block_id, block_id)
        elif not is_genesis:
            store.db.insert_orphan_block(block_id, store.hashin(b['hashPrev']))

        for row in store.db.get_orphan_block_id(store.hashin(b['hash'])):
            (orphan_id,) = row
            store.db.update_prev_block_id(block_id, orphan_id)
            store.db.insert_block_next(block_id, orphan_id)
            store.db.delete_orphan_block(orphan_id)
            
        # 处理孤儿块的问题
        store.offer_block_to_chains(b, chain.id)
        return block_id


    def import_tx(store, tx, is_coinbase, chain):
        
        tx_id    = store.new_id("tx")
        dbhash   = store.hashin(tx['hash'])
        version  = store.intin(tx['version'])
        locktime = store.intin(tx['lockTime'])
        
        if 'size' not in tx:
            tx['size'] = len(tx['__data__'])

        store.db.insert_tx(tx_id, dbhash, version, locktime, tx['size']) 
    
        # 导入交易的 outputs.
        tx['value_out'] = 0
        tx['value_destroyed'] = 0
        for pos in xrange(len(tx['txOut'])):
            txout = tx['txOut'][pos]
            tx['value_out'] += txout['value']
            txout_id = store.new_id("txout")

            pubkey_id = store.script_to_pubkey_id(chain, txout['scriptPubKey'])
            if pubkey_id is not None and pubkey_id <= 0:
                tx['value_destroyed'] += txout['value']


            txout_value = store.intin(txout['value'])
            scriptPubkey = store.binin(txout['scriptPubKey'])
            store.db.insert_txout(txout_id, tx_id, pos, txout_value, scriptPubkey, pubkey_id)
            
            for row in store.db.get_txin_by_txout_pos(dbhash, pos):  
                (txin_id,) = row
                store.db.update_txin(txout_id, txin_id)
                store.db.delete_unlinked_txin(txin_id)

        # 导入交易的inputs.
        tx['value_in'] = 0
        tx['unlinked_count'] = 0
        for pos in xrange(len(tx['txIn'])):
            txin = tx['txIn'][pos]
            txin_id = store.new_id("txin")

            if is_coinbase:
                txout_id = None
            else:
                prevout_hash = store.hashin(txin['prevout_hash'])
                txout_id, value = store.db.lookup_txout(prevout_hash, txin['prevout_n'])
                if value is None:
                    tx['value_in'] = None
                elif tx['value_in'] is not None:
                    tx['value_in'] += value


            sequence = store.intin(txin['sequence'])
            scriptSig = store.binin(txin['scriptSig'])        
            store.db.insert_txin(txin_id, tx_id, pos, txout_id, scriptSig, sequence)
            
            if not is_coinbase and txout_id is None:
                tx['unlinked_count'] += 1
                prev_hash = store.hashin(txin['prevout_hash'])
                prev_n = store.intin(txin['prevout_n'])
                store.db.insert_unlinked_txin(txin_id, prev_hash, prev_n)
  
        return tx_id

    def offer_block_to_chains(store, b, chain_ids):
        b['top'] = store.adopt_orphans(b, 0, chain_ids, chain_ids)
        for chain_id in chain_ids:
            store._offer_block_to_chain(b, chain_id)
    
    def populate_block_txin(store, block_id):
            
        rows = store.db.get_block_txin(block_id) 
        for row in rows:
            (txin_id, oblock_id) = row
            if store.is_descended_from(block_id, int(oblock_id)):
                store.db.insert_block_txin(block_id, txin_id, oblock_id)
    
    
    def is_descended_from(store, block_id, ancestor_id):
        block = store.load_block(block_id)
        ancestor = store.load_block(ancestor_id)
        height = ancestor['height']
        return block['height'] >= height and \
            store.get_block_id_at_height(height, block_id) == ancestor_id
    
    
    def script_to_pubkey_id(store, chain, script):
        script_type, data = chain.parse_txout_script(script)

        if script_type in (Chain.SCRIPT_TYPE_ADDRESS, Chain.SCRIPT_TYPE_P2SH):
            return store.pubkey_hash_to_id(data)

        if script_type == Chain.SCRIPT_TYPE_PUBKEY:
            return store.pubkey_to_id(chain, data)

        if script_type == Chain.SCRIPT_TYPE_MULTISIG:
            script_hash = chain.script_hash(script)
            multisig_id = store._pubkey_id(script_hash, script)

            if not store.selectrow("SELECT 1 FROM multisig_pubkey WHERE multisig_id = ?", (multisig_id,)):
                for pubkey in set(data['pubkeys']):
                    pubkey_id = store.pubkey_to_id(chain, pubkey)
                    store.sql("""
                        INSERT INTO multisig_pubkey (multisig_id, pubkey_id)
                        VALUES (?, ?)""", (multisig_id, pubkey_id))
            return multisig_id

        if script_type == Chain.SCRIPT_TYPE_BURN:
            return PUBKEY_ID_NETWORK_FEE

        return None

    def pubkey_hash_to_id(store, pubkey_hash):
        return tore._pubkey_id(pubkey_hash, None)
    
    def pubkey_to_id(store, chain, pubkey):
        pubkey_hash = chain.pubkey_hash(pubkey)
        return store._pubkey_id(pubkey_hash, pubkey)

    
    def _pubkey_id(store, pubkey_hash, pubkey):
        dbhash = store.binin(pubkey_hash)
        pubkey_id = store.db.get_pubkey_id(dbhash)
        if pubkey_id:
            return pubkey_id
        else:
            pubkey_id = store.new_id("pubkey")
            if pubkey is not None and len(pubkey) > MAX_PUBKEY:
                pubkey = None
            store.db.insert_pubkey(pubkey_id, dbhash, store.binin(pubkey))
            return pubkey_id
    
    
    
    def adopt_orphans(store, b, orphan_work, chain_ids, chain_mask):

        ret = [None]
        def receive(x):
            ret[0] = x
        def doit():
            store._adopt_orphans_1(stack)
        stack = [receive, chain_mask, chain_ids, orphan_work, b, doit]
        while stack:
            stack.pop()()
        return ret[0]
        
    def _adopt_orphans_1(store, stack):
        def doit():
            store._adopt_orphans_1(stack)
        def continuation(x):
            store._adopt_orphans_2(stack, x)
        def didit():
            ret = stack.pop()
            stack.pop()(ret)

        b = stack.pop()
        orphan_work = stack.pop()
        chain_ids = stack.pop()
        chain_mask = stack.pop()
        ret = {}
        stack += [ ret, didit ]

        block_id = b['block_id']
        # 下一个高度
        height = None if b['height'] is None else int(b['height'] + 1)


        ret[chain_id] = (b, orphan_work)
        
        #下一个区块的
        for row in store.db.get_next_block(block_id):
                        
            next_id, nBits, value_out, value_in, nTime, satoshis = row
            nBits = int(nBits)
            nTime = int(nTime)
            satoshis = None if satoshis is None else int(satoshis)
            new_work = util.calculate_work(orphan_work, nBits)

            if b['chain_work'] is None:
                chain_work = None
            else:
                chain_work = b['chain_work'] + new_work - orphan_work

            if value_in is None:
                value, count1, count2 = store.db.get_block_tx_info(next_id)
                if count1 == count2 + 1:
                    value_in = int(value)
                else:
                    LOG.debug(
                        "not updating block %d value_in: %s != %s + 1",
                        next_id, repr(count1), repr(count2))
            else:
                value_in = int(value_in)
            generated = None if value_in is None else int(value_out - value_in)

            if b['seconds'] is None:
                seconds = None
                total_ss = None
            else:
                new_seconds = nTime - b['nTime']
                seconds = b['seconds'] + new_seconds
                if b['total_ss'] is None or b['satoshis'] is None:
                    total_ss = None
                else:
                    total_ss = b['total_ss'] + new_seconds * b['satoshis']

            if satoshis < 0 and b['satoshis'] is not None and \
                    b['satoshis'] >= 0 and generated is not None:
                satoshis += 1 + b['satoshis'] + generated

            if height is None or height < 2:
                search_block_id = None
            else:
                search_block_id = store.get_block_id_at_height(util.get_search_height(height), int(block_id))

            
            store.db.update_block(height, store.binin_int(chain_work, WORK_BITS),
                                  store.intin(value_in),
                                  store.intin(seconds), store.intin(satoshis),
                                  store.intin(total_ss), search_block_id,
                                  next_id)

            ss = None

            if height is not None:
                
                store.db.update_candidate(height, next_id)
                store.populate_block_txin(int(next_id))

                if b['ss'] is None or store.db.get_unlinked_txins(next_id):
                    pass
                else:
                    tx_ids = map(lambda row: row[0], store.db.get_block_txids(next_id))
                    destroyed = store.db.get_block_ss_destroyed(next_id, nTime, tx_ids)
                    ss = b['ss'] + b['satoshis'] * (nTime - b['nTime']) - destroyed
                    
                    store.db.update_block_ss(store.intin(ss),store.intin(destroyed),next_id)
      
            nb = {
                "block_id": next_id,
                "height": height,
                "chain_work": chain_work,
                "nTime": nTime,
                "seconds": seconds,
                "satoshis": satoshis,
                "total_ss": total_ss,
                "ss": ss}

            stack += [ret, continuation,
                      chain_mask, None, new_work, nb, doit]
            
            
    def _adopt_orphans_2(store, stack, next_ret):
        ret = stack.pop()
        for chain_id in ret.keys():
            pair = next_ret[chain_id]
            if pair and pair[1] > ret[chain_id][1]:
                ret[chain_id] = pair


    def _offer_block_to_chain(store, b, chain_id):
        if b['chain_work'] is None:
            in_longest = 0
        else:
            top = b['top'][chain_id][0]
            row = store.db.get_block_by_chain(chain_id)
            
            if row:
                loser_id, loser_height, loser_work = row
                if loser_id != top['block_id'] and \
                        store.binout_int(loser_work) >= top['chain_work']:
                    row = None
            if row:
                # New longest chain.
                in_longest = 1
                to_connect = []
                to_disconnect = []
                winner_id = top['block_id']
                winner_height = top['height']
                while loser_height > winner_height:
                    to_disconnect.insert(0, loser_id)
                    loser_id = store.db.get_prev_block_id(loser_id)
                    loser_height -= 1
                while winner_height > loser_height:
                    to_connect.insert(0, winner_id)
                    winner_id = store.db.get_prev_block_id(winner_id)
                    winner_height -= 1
                loser_height = None
                while loser_id != winner_id:
                    to_disconnect.insert(0, loser_id)
                    loser_id = store.db.get_prev_block_id(loser_id)
                    to_connect.insert(0, winner_id)
                    winner_id = store.db.get_prev_block_id(winner_id)
                    winner_height -= 1
                for block_id in to_disconnect:
                    store.db.disconnect_block(block_id, chain_id)
                for block_id in to_connect:
                    store.db.connect_block(block_id, chain_id)

            elif b['hashPrev'] == store.chains_by.id[chain_id].genesis_hash_prev:
                in_longest = 1  # Assume only one genesis block per chain.  XXX
            else:
                in_longest = 0

        store.db.insert_candidate(chain_id, b,in_longest)
        if in_longest > 0:
            store.db.update_chain(top['block_id'], chain_id)



    def offer_existing_block(store, hash, chain_Id):
        block_row = store.db.get_block_by_hash(store.hashin(hash))
        if not block_row:
            return False
 
        b = {
            "block_id":   block_row[0],
            "height":     block_row[1],
            "chain_work": store.binout_int(block_row[2]),
            "nTime":      block_row[3],
            "seconds":    block_row[4],
            "satoshis":   block_row[5],
            "ss":         block_row[6],
            "total_ss":   block_row[7]}

        if store.db.exist_candidate(b['block_id'], chain_id):
            LOG.info("block %d already in chain %d", b['block_id'], chain_id)
        else:
            if b['height'] == 0:
                b['hashPrev'] = store.chains_by.id[chain_id].genesis_hash_prev
            else:
                b['hashPrev'] = 'dummy'  # Fool adopt_orphans.
            store.offer_block_to_chains(b, [chain_id, ])
        return True


    def init_binfuncs(store):
        store.binin       = util.identity
        store.binin_hex   = util.from_hex
        store.binin_int   = util.binin_int
        store.binout      = util.identity
        store.binout_hex  = util.to_hex
        store.binout_int  = util.binout_int
        store.intin       = util.identity
        store.hashin      = util.rev
        store.hashin_hex  = util.from_hex
        store.hashout     = util.rev
        store.hashout_hex = util.to_hex
        
    
    def get_block_id_at_height(store, height, descendant_id):
        if height is None:
            return None
        while True:
            block = store.load_block(descendant_id)
            if block['height'] == height:
                return descendant_id
            descendant_id = block[
                'search_id'
                if util.get_search_height(block['height']) >= height else
                'prev_id']

    def cache_block(store, block_id, height, prev_id, search_id):
        assert isinstance(block_id, int), block_id
        assert isinstance(height, int), height
        assert prev_id is None or isinstance(prev_id, int)
        assert search_id is None or isinstance(search_id, int)
        block = {
            'height':    height,
            'prev_id':   prev_id,
            'search_id': search_id}
        store._blocks[block_id] = block
        return block

    def load_block(store, block_id):
        block = store._blocks.get(block_id)
        if block is None:
            
            row = store.db.get_block_id_by_height(block_id)
            if row is None:
                return None
            height, prev_id, search_id = row
            block = store.cache_block(
                block_id, int(height),
                None if prev_id is None else int(prev_id),
                None if search_id is None else int(search_id))
        return block
    
        
    def new_id(store, key):
        return store.db.new_id(key)
 
 
    def flush(store):
        if store.bytes_since_commit > 0:
            store.db.commit()
            LOG.debug("commit")
            store.bytes_since_commit = 0

    def rollback(store):
        store.db.rollback()
    
    def commit(store):
        store.db.commit()
    
    def get_block_number(store):
        return store.db.get_block_height()
 